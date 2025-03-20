import typing

import click

from ..utils.printer import print_result

if typing.TYPE_CHECKING:
    from ..client import Primitive

from rich.console import Console
from rich.table import Table


@click.group()
@click.pass_context
def cli(context):
    """Hardware"""
    pass


@cli.command("systeminfo")
@click.pass_context
def systeminfo_command(context):
    """Get System Info"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.hardware.get_system_info()
    print_result(message=message, context=context)


@cli.command("register")
@click.pass_context
def register_command(context):
    """Register Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    result = primitive.hardware.register()
    color = "green" if result else "red"
    if result.data.get("registerHardware"):
        message = "Hardware registered successfully"
    else:
        message = (
            "There was an error registering this device. Please review the above logs."
        )
    print_result(message=message, context=context, fg=color)


@cli.command("unregister")
@click.pass_context
def unregister_command(context):
    """Unregister Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    result = primitive.hardware.unregister()
    color = "green" if result else "red"
    if not result:
        message = "There was an error unregistering this device. Please review the above logs."
        return
    elif result.data.get("unregisterHardware"):
        message = "Hardware unregistered successfully"
    print_result(message=message, context=context, fg=color)


@cli.command("checkin")
@click.pass_context
def checkin_command(context):
    """Checkin Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    check_in_http_result = primitive.hardware.check_in_http()
    if messages := check_in_http_result.data.get("checkIn").get("messages"):
        print_result(message=messages, context=context, fg="yellow")
    else:
        message = "Hardware checked in successfully"
        print_result(message=message, context=context, fg="green")


def hardware_status_string(hardware):
    if activeReservation := hardware.get("activeReservation"):
        if activeReservation.get("status", None) == "in_progress":
            return "Reserved"
    if hardware.get("isQuarantined"):
        return "Quarantined"
    if not hardware.get("isOnline"):
        return "Offline"
    if not hardware.get("isHealthy"):
        return "Not healthy"
    if not hardware.get("isAvailable"):
        return "Not available"
    else:
        return "Available"


def render_hardware_table(hardware_list):
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Organization")
    table.add_column("Name | Slug")
    table.add_column("Status")
    table.add_column("Reservation")

    for hardware in hardware_list:
        name = hardware.get("name")
        slug = hardware.get("slug")
        print_name = name
        if name != slug:
            print_name = f"{name} | {slug}"
        child_table = Table(show_header=False, header_style="bold magenta")
        child_table.add_column("Organization")
        child_table.add_column("Name | Slug")
        child_table.add_column("Status")
        child_table.add_column("Reservation", justify="right")

        table.add_row(
            hardware.get("organization").get("name"),
            print_name,
            hardware_status_string(hardware),
            f"{hardware.get('activeReservation').get('createdBy').get('username')} | {hardware.get('activeReservation').get('status')}"
            if hardware.get("activeReservation", None)
            else "",
        )

        if len(hardware.get("children", [])) > 0:
            for child in hardware.get("children"):
                name = child.get("name")
                slug = child.get("slug")
                print_name = name
                if name != slug:
                    print_name = f"└── {name} | {slug}"
                table.add_row(
                    hardware.get("organization").get("name"),
                    print_name,
                    hardware_status_string(hardware),
                    f"{hardware.get('activeReservation').get('createdBy').get('username')} | {hardware.get('activeReservation').get('status')}"
                    if hardware.get("activeReservation", None)
                    else "",
                )

    console.print(table)


@cli.command("list")
@click.pass_context
def list_command(context):
    """List Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    get_hardware_list_result = primitive.hardware.get_hardware_list(
        nested_children=True
    )

    hardware_list = [
        hardware.get("node")
        for hardware in get_hardware_list_result.data.get("hardwareList").get("edges")
    ]

    if context.obj["JSON"]:
        print_result(message=hardware_list, context=context)
        return
    else:
        render_hardware_table(hardware_list)


@cli.command("get")
@click.pass_context
@click.argument(
    "hardware_identifier",
    type=str,
    required=True,
)
def get_command(context, hardware_identifier: str) -> None:
    """Get Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    hardware = primitive.hardware.get_hardware_from_slug_or_id(
        hardware_identifier=hardware_identifier
    )

    if context.obj["JSON"]:
        print_result(message=hardware, context=context)
        return
    else:
        render_hardware_table([hardware])
