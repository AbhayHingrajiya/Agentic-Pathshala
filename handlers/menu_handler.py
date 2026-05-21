from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from utils.validator import validate_menu_choice


class MenuHandler:
    def __init__(self, console: Console) -> None:
        self.console = console

    def display_menu(self) -> None:
        table = Table(
            title="📚 Main Menu",
            box=box.ROUNDED,
            border_style="cyan",
            show_lines=True,
        )
        table.add_column("Option", style="bold green", justify="center")
        table.add_column("Feature", style="bold white")

        table.add_row("1", "Chat with AI")
        table.add_row("2", "Exit Application")

        self.console.print(table)

    def prompt_choice(self) -> str:
        choice = Prompt.ask("\n[bold cyan]Enter your choice[/bold cyan]", default="1").strip()
        if not validate_menu_choice(choice, 1, 2):
            self.console.print("❌ Invalid choice! Please enter 1 or 2.")
            return ""
        return choice
