import sys

from opentelemetry import context
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box, json
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
        table.add_row("5", "Evaluator")
        table.add_row("6", "Exit Application")

        console.print(table)

    def run(self, learner):
        """Main application loop"""

        while True:

            self.display_menu()

            choice = Prompt.ask(
                "\n[bold cyan]Enter your choice[/bold cyan]",
                default="1"
            ).strip()

            if not choice.isdigit() or not (1 <= int(choice) <= 6):

                console.print(
                    "[bold red]❌ Invalid choice! Please enter 1-6.[/bold red]\n"
                )

                continue

            user_prompt = None

            if 2 <= int(choice) <= 5 and int(choice ) != 5:

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

                # with console.status(
                #     "[bold magenta]🔍 Processing hybrid search...[/bold magenta]",
                #     spinner="earth"
                # ):

                user_prompt = f"always return 'assessment_query' : {user_prompt}"
                initial_state = {
                    "user_input": user_prompt,
                    "learner_id": learner["learner_id"],
                    "execution_path": []
                }
                
                response = graph.invoke(initial_state)

                console.print("\n[bold cyan]🤖 Assessment[/bold cyan]")
                
                try:
                    assessment_questions = json.loads(response.get("agent_response", "[]"))
                except Exception as e:
                    console.print("[bold red]❌ Error decoding assessment questions![/bold red]")
                    assessment_questions = []
                    
                if response.get("agent_response") and assessment_questions is not None:

                    for idx, question_data in enumerate(assessment_questions, start=1):

                        console.print(
                            Panel(
                                question_data["question"],
                                title=f"[bold yellow]Question {idx}[/bold yellow]",
                                border_style="yellow",
                                padding=(1, 2)
                            )
                        )

                        learner_answer = Prompt.ask(
                            "[bold cyan]Enter your answer[/bold cyan]"
                        ).strip()

                        question_data["answer"] = learner_answer

                    # console.print("\n[bold green]Assessment Summary[/bold green]\n")

                    # for idx, question_data in enumerate(assessment_questions, start=1):

                    #     panel_content = (
                    #         f"{question_data['question']}\n\n"
                    #         f"[bold green]Learner Answer:[/bold green] "
                    #         f"{question_data['answer']}"
                    #     )

                    #     console.print(
                    #         Panel(
                    #             panel_content,
                    #             title=f"[bold yellow]Q{idx}[/bold yellow]",
                    #             border_style="green",
                    #             padding=(1, 2)
                    #         )
                    #     )
                
                if response.get("agent_response") and assessment_questions is not None:
                      
                    assessment_questions_string = json.dumps(
                        assessment_questions,
                        indent=4
                    )     
                     
                    assessment_questions_string = f"always return 'evaluator_query' : {assessment_questions_string}"
                    initial_state = {
                        "user_input": assessment_questions_string,
                        "learner_id": learner["learner_id"],
                        "execution_path": []
                    }
                    
                    response = graph.invoke(initial_state)

                    console.print("\n[bold cyan]🤖 Evaluator[/bold cyan]")
                    
                    if "agent_response" in response:
                        console.print(response["agent_response"])
                    else:
                        console.print("[red]Something went wrong with the graph![/red]")
                        
                    console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(response.get('execution_path', []))}[/dim italic]\n")

                else:
                    console.print(
                        "[bold red]Something went wrong while fetching assessment questions![/bold red]"
                    )
                    
                console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(response.get('execution_path', []))}[/dim italic]\n")

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

                # with console.status(
                #     "[bold magenta]🔍 Processing hybrid search...[/bold magenta]",
                #     spinner="earth"
                # ):

                print("\n[bold yellow]Enter your prompt (type END on new line to finish)[/bold yellow]")

                lines = []

                while True:
                    line = input()

                    if line.strip().upper() == "END":
                        break

                    lines.append(line)

                user_prompt = "\n".join(lines).strip()

                user_prompt = f"always return 'evaluator_query' : {user_prompt}"
                initial_state = {
                    "user_input": user_prompt,
                    "learner_id": learner["learner_id"],
                    "execution_path": []
                }
                
                response = graph.invoke(initial_state)

                console.print("\n[bold cyan]🤖 Evaluator[/bold cyan]")
                
                if "agent_response" in response:
                    console.print(response["agent_response"])
                else:
                    console.print("[red]Something went wrong with the graph![/red]")
                    
                console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(response.get('execution_path', []))}[/dim italic]\n")
                    
            elif choice == "6":

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