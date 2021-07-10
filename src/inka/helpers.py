from rich.console import Console

from inka.models.notes.note import Note

CONSOLE = Console()


def print_result(msg: str) -> None:
    CONSOLE.print(f"{msg}", style="green")


def print_action(msg: str) -> None:
    CONSOLE.print(f"[cyan1]::[/cyan1] {msg}", style="bold")


def print_error(message: str, pause: bool = False, note: Note = None) -> None:
    if note:
        CONSOLE.print(note)
    CONSOLE.print(f"ERROR: {message}", style="red bold")

    if pause:
        CONSOLE.input("Press [italic]Enter[/italic] to continue...\n")


def print_sub_error(msg: str) -> None:
    CONSOLE.print(f"   {msg}", style="red")


def print_warning(message: str) -> None:
    CONSOLE.print(f"WARNING: {message}", style="yellow bold")


def print_sub_warning(msg: str) -> None:
    CONSOLE.print(f"   {msg}", style="yellow")


def print_step(msg: str) -> None:
    CONSOLE.print(f"[green]==>[/green] {msg}", style="bold")


def print_sub_step(msg: str) -> None:
    CONSOLE.print(f"  [cyan1]->[/cyan1] {msg}")
