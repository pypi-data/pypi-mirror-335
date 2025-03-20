import os
import typing
import re
import shutil
from typing import Dict, TypedDict, List
from abc import abstractmethod
from enum import IntEnum, Enum
from pathlib import Path, PurePath
from loguru import logger
import yaml
import asyncio
from primitive.utils.shell import env_string_to_dict
from ..utils.cache import get_artifacts_cache, get_sources_cache, get_logs_cache

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

if typing.TYPE_CHECKING:
    import primitive.client

ENV_VAR_LOOKUP_START = "_ENV_VAR_LOOKUP_START"
ENV_VAR_LOOKUP_END = "_ENV_VAR_LOOKUP_END"


class Task(TypedDict):
    label: str
    workdir: str
    tags: Dict
    cmd: str


class JobConfig(TypedDict):
    requires: List[str]
    executes: List[Task]
    stores: List[str]


# NOTE This must match FailureLevel subclass in JobSettings model
class FailureLevel(IntEnum):
    ERROR = 1
    WARNING = 2


class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"


class Runner:
    def __init__(
        self,
        primitive: "primitive.client.Primitive",
        job_run: Dict,
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> None:
        self.primitive = primitive
        self.job = job_run["job"]
        self.job_run = job_run
        self.job_settings = job_run["jobSettings"]
        self.config = None
        self.source_dir = None
        self.initial_env = {}
        self.modified_env = {}
        self.file_logger = None

        logger.enable("primitive")

        # If max_log_size set to <= 0, disable file logging
        if max_log_size > 0:
            log_name = f"{self.job['slug']}_{self.job_run['jobRunNumber']}_{{time}}.primitive.log"

            self.file_logger = logger.add(
                Path(get_logs_cache(self.job_run["id"]) / log_name),
                rotation=max_log_size,
                format=Runner.fmt,
                backtrace=True,
                diagnose=True,
            )

    def setup(self) -> None:
        # Attempt to download the job source code
        git_repo_full_name = self.job_run["gitCommit"]["repoFullName"]
        git_ref = self.job_run["gitCommit"]["sha"]
        logger.info(f"Downloading repository {git_repo_full_name} at ref {git_ref}")

        github_access_token = self.primitive.jobs.github_access_token_for_job_run(
            self.job_run["id"]
        )

        downloaded_git_repository_dir = (
            self.primitive.git.download_git_repository_at_ref(
                git_repo_full_name=git_repo_full_name,
                git_ref=git_ref,
                github_access_token=github_access_token,
                destination=get_sources_cache(),
            )
        )

        self.source_dir = downloaded_git_repository_dir.joinpath(
            self.job_settings["rootDirectory"]
        )

        # Attempt to parse the job yaml file
        logger.info(f"Scanning directory for job file {self.job['slug']}")
        yaml_file = Path(self.source_dir / ".primitive" / f"{self.job['slug']}.yaml")
        yml_file = Path(self.source_dir / ".primitive" / f"{self.job['slug']}.yml")

        if yaml_file.exists() and yml_file.exists():
            logger.error(
                f"Found two job descriptions with the same slug: {self.job['slug']}"
            )
            raise FileExistsError

        if yaml_file.exists() or yml_file.exists():
            logger.info(f"Found job description for {self.job['slug']}")
            config_file = yaml_file if yaml_file.exists() else yml_file
            self.config = yaml.load(open(config_file, "r"), Loader=Loader)[
                self.job["name"]
            ]
        else:
            logger.error(
                f"No job description with matching slug '{self.job['slug']}' found"
            )
            raise FileNotFoundError

        # Setup initial process environment
        self.initial_env = os.environ
        self.initial_env["PRIMITIVE_GIT_SHA"] = str(self.job_run["gitCommit"]["sha"])
        self.initial_env["PRIMITIVE_GIT_BRANCH"] = str(
            self.job_run["gitCommit"]["branch"]
        )
        self.initial_env["PRIMITIVE_GIT_REPO"] = str(
            self.job_run["gitCommit"]["repoFullName"]
        )

    def execute(self) -> None:
        logger.info(f"Executing {self.job['slug']} job")
        self.primitive.jobs.job_run_update(
            self.job_run["id"], status="request_in_progress"
        )
        self.modified_env = {**self.initial_env}

        task_failed = False
        for task in self.config["executes"]:
            with logger.contextualize(label=task["label"]):
                with asyncio.Runner() as async_runner:
                    if task_failed := async_runner.run(self.run_task(task)):
                        break

        if not task_failed:
            self.primitive.jobs.job_run_update(
                self.job_run["id"], status="request_completed", conclusion="success"
            )
            logger.success(f"Completed {self.job['slug']} job")

    async def run_task(self, task: Task) -> bool:
        for cmd in task["cmd"].strip().split("\n"):
            args = [
                "/bin/bash",
                "-c",
                f"{cmd} && echo '{ENV_VAR_LOOKUP_START}' && env && echo '{ENV_VAR_LOOKUP_END}'",
            ]

            process = await asyncio.create_subprocess_exec(
                *args,
                env=self.modified_env,
                cwd=str(Path(self.source_dir / task.get("workdir", ""))),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_failed, stderr_failed, cancelled = await asyncio.gather(
                self.log_cmd(
                    process=process, stream=process.stdout, tags=task.get("tags", {})
                ),
                self.log_cmd(
                    process=process, stream=process.stderr, tags=task.get("tags", {})
                ),
                asyncio.create_task(self.monitor_cmd(process=process)),
            )

            returncode = await process.wait()

            if cancelled:
                return True

            if returncode > 0 or stdout_failed or stderr_failed:
                await self.primitive.jobs.ajob_run_update(
                    self.job_run["id"], status="request_completed", conclusion="failure"
                )

                if returncode > 0:
                    logger.error(
                        f"Task {task['label']} failed on '{cmd}' with return code {returncode}"
                    )
                else:
                    logger.error(f"Task {task['label']} failed on '{cmd}'")

                return True

        return False

    async def log_cmd(self, process, stream, tags: Dict = {}) -> bool:
        failure_detected = False
        while line := await stream.readline():
            raw_data = line.decode()

            # handle env vars
            if ENV_VAR_LOOKUP_START in raw_data:
                env_vars_string = ""
                while env_line := await stream.readline():
                    if ENV_VAR_LOOKUP_END in env_line.decode():
                        break
                    env_vars_string += env_line.decode()

                self.modified_env = env_string_to_dict(env_vars_string)
                continue

            # Handle logging
            parse_logs = self.job_settings["parseLogs"]
            parse_stderr = self.job_settings["parseStderr"]

            level = LogLevel.INFO
            tag = None
            if (parse_logs and "error" in raw_data.lower()) or (
                parse_stderr and stream is process.stderr
            ):
                level = LogLevel.ERROR
            elif parse_logs and "warning" in raw_data.lower():
                level = LogLevel.WARNING

            failure_detected = (
                level == LogLevel.ERROR
                and self.job_settings["failureLevel"] >= FailureLevel.ERROR
            ) or (
                level == LogLevel.WARNING
                and self.job_settings["failureLevel"] >= FailureLevel.WARNING
            )

            # Tag on the first matching regex in the list
            for tag_key, regex in tags.items():
                pattern = re.compile(regex)
                if pattern.match(raw_data):
                    tag = tag_key
                    break

            logger.bind(tag=tag).log(level.value, raw_data.rstrip())

        return failure_detected

    async def monitor_cmd(self, process) -> bool:
        while process.returncode is None:
            status = await self.primitive.jobs.aget_job_status(self.job_run["id"])
            status_value = status.data["jobRun"]["status"]
            conclusion_value = status.data["jobRun"]["conclusion"]

            if status_value == "completed" and conclusion_value == "cancelled":
                logger.warning("Job cancelled by user")
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass

                return True

            await asyncio.sleep(5)

        return False

    def cleanup(self) -> None:
        logger.remove(self.file_logger)

        if "stores" not in self.config:
            return

        for glob in self.config["stores"]:
            path = Path(glob)

            if path.is_dir():
                files = [str(f) for f in path.rglob("*") if f.is_file()]
            else:
                files = [str(f) for f in Path().glob(glob) if f.is_file()]

            for file in files:
                relative_path = PurePath(file).relative_to(self.source_dir)
                destination = Path(
                    get_artifacts_cache(self.job_run["id"]) / relative_path
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                Path(file).replace(destination)

        shutil.rmtree(path=self.source_dir)

    @abstractmethod
    def fmt(record) -> str:
        extra = record["extra"]
        # Delimiters with empty space MUST exist for LogQL pattern matching
        label = extra.get("label", None)
        tag = extra.get("tag", None)
        context = f"{label} | " if label else " | "
        context += f"{tag} | " if tag else " | "

        log = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS!UTC}</green> | "
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            f"{context}"
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>\n"
        )

        return log
