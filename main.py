import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align
from rich.status import Status

from UI.menu_handler import MenuHandler
from auth.login_handler import LoginHandler
from UI.assignment_handler import AssignmentHandler
from orchestrator import graph


console = Console()


class MainApp:

    def __init__(self):

        # Initialize handlers
        self.menu_handler = MenuHandler()
        self.login_handler = LoginHandler()
        self.assignment_handler = AssignmentHandler()

    def show_banner(self):
        """Display application banner"""

        banner = Text(
            "🎓 Agentic Pathshala - AI Learning Coach",
            style="bold cyan"
        )

        console.print(
            Panel(
                Align.center(banner),
                border_style="bright_blue",
                padding=(1, 2),
                box=box.DOUBLE,
            )
        )

    def login(self):
        """Handle user login"""

        self.show_banner()

        console.print("\n[bold yellow]🔐 Login Required[/bold yellow]\n")

        learner = self.login_handler.login()

        if not learner:
            console.print(
                "\n[bold red]❌ Login failed! Exiting application.[/bold red]"
            )
            sys.exit(1)

        console.print(
            f"\n[bold green]✅ Welcome {learner['name']}![/bold green]\n"
        )

        self.run(learner)

        return learner

    def display_menu(self):
        """Display styled menu"""

        table = Table(
            title="📚 Main Menu",
            box=box.ROUNDED,
            border_style="cyan",
            show_lines=True
        )

        table.add_column("Option", style="bold green", justify="center")
        table.add_column("Feature", style="bold white")

        table.add_row("1", "Assigned Assignment")
        table.add_row("2", "Available Assignements")
        table.add_row("3", "Assessment")
        table.add_row("4", "Chat with AI")
        table.add_row("5", "Exit Application")

        console.print(table)

    def run(self, learner):
        """Main application loop"""

        while True:

            self.display_menu()

            choice = Prompt.ask(
                "\n[bold cyan]Enter your choice[/bold cyan]",
                default="1"
            ).strip()

            if not choice.isdigit() or not (1 <= int(choice) <= 5):

                console.print(
                    "[bold red]❌ Invalid choice! Please enter 1-5.[/bold red]\n"
                )

                continue

            user_prompt = None

            if 2 <= int(choice) <= 4:

                user_prompt = Prompt.ask(
                    "\n[bold yellow]Enter your prompt[/bold yellow]"
                ).strip()

                if not user_prompt:

                    console.print(
                        "[bold red]❌ Prompt cannot be empty![/bold red]\n"
                    )

                    continue

            if choice == "1":

                console.print(
                    "\n[bold blue]📂 Fetching assignments...[/bold blue]\n"
                )

                self.assignment_handler.view_assigned_assignments(
                    learner["learner_id"]
                )

            elif choice == "2":

                with console.status(
                    "[bold green]🤖 AI is thinking...[/bold green]",
                    spinner="dots"
                ):

                    self.assignment_handler.view_available_assignments(
                        learner["learner_id"]
                    )

            elif choice == "3":

                with console.status(
                    "[bold magenta]🔍 Processing hybrid search...[/bold magenta]",
                    spinner="earth"
                ):

                    self.question_handler.ask_question_hybrid(
                        user_prompt
                    )

            elif choice == "4":

                with console.status(
                    "[bold magenta]🧠 AI Coach is thinking...[/bold magenta]",
                    spinner="dots"
                ):
                    
                    initial_state = {
                        "user_input": user_prompt,
                        "learner_id": learner["learner_id"],
                        "execution_path": []
                    }
                    
                    response = graph.invoke(initial_state)

                    console.print("\n[bold cyan]🤖 AI Coach:[/bold cyan]")
                    
                    if "agent_response" in response:
                        console.print(response["agent_response"])
                    else:
                        console.print("[red]Something went wrong with the graph![/red]")
                        
                    console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(response.get('execution_path', []))}[/dim italic]\n")

            elif choice == "5":

                console.print(
                    Panel(
                        "[bold green]🙏 Thank you for using Agentic Pathshala![/bold green]",
                        border_style="green",
                        padding=(1, 2)
                    )
                )

                sys.exit(0)

            else:

                console.print(
                    "[bold red]❌ Invalid option selected.[/bold red]"
                )


if __name__ == "__main__":
    app = MainApp()
    app.login()
    
# def main():
#     while True:
        
#         user_input = input("You: ")
#         if user_input.lower() == "exit":
#             break

#         response = graph.invoke({"user_input": user_input})
#         print("Execution Path:", response["execution_path"])
#         print("AI:", response["tool_result"])
        

# if __name__ == "__main__":
#     main()