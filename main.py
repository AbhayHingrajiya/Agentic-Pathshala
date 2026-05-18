import sys
from typing import Optional

from rich.align import Align
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from config.settings import settings
from handlers.assignment_handler import AssignmentHandler
from handlers.login_handler import LoginHandler
from handlers.menu_handler import MenuHandler
from rag.ingestion import ingest_documents
from repositories.assignment_repository import AssignmentRepository
from repositories.learner_repository import LearnerRepository
from services.ai_service import AIService
from services.assignment_service import AssignmentService
from services.auth_service import AuthService
from utils.logger import get_logger
from utils.validator import is_non_empty_string

console = Console()
logger = get_logger(__name__)


class MainApp:
    def __init__(self) -> None:
        learner_repository = LearnerRepository()
        assignment_repository = AssignmentRepository()

        auth_service = AuthService(learner_repository)
        assignment_service = AssignmentService(assignment_repository)
        self.ai_service = AIService()

        self.menu_handler = MenuHandler(console)
        self.login_handler = LoginHandler(auth_service, console)
        self.assignment_handler = AssignmentHandler(assignment_service, console)
        ingest_documents()

        logger.info("Configuration loaded from %s", settings.MCP_SERVER_URL)

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

    def login(self) -> Optional[object]:
        self.show_banner()
        console.print("\n[bold yellow]🔐 Login Required[/bold yellow]\n")

        learner = self.login_handler.login()
        if learner is None:
            console.print("\n[bold red]❌ Login failed![/bold red]")
            self.login()

        console.print(f"\n[bold green]✅ Welcome {learner.name}![/bold green]\n")
        self.run(learner)
        return learner

    def _request_user_prompt(self) -> Optional[str]:
        user_prompt = Prompt.ask("\n[bold yellow]Enter your prompt[/bold yellow]").strip()
        if not is_non_empty_string(user_prompt):
            console.print("[bold red]❌ Prompt cannot be empty![/bold red]\n")
            return None
        return user_prompt

    def _display_agent_response(self, response: dict) -> None:
        if agent_response := response.get("agent_response"):
            console.print(agent_response)
        else:
            console.print("[red]Something went wrong with the graph![/red]")

        execution_path = response.get("execution_path", [])
        console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(execution_path)}[/dim italic]\n")

    def _handle_assessment(self, learner: object) -> None:
        user_prompt = self._request_user_prompt()
        if user_prompt is None:
            return

        response = self.ai_service.run_assessment(user_prompt, learner.learner_id)
        console.print("\n[bold cyan]🤖 Assessment[/bold cyan]")

        assessment_questions = self.ai_service.parse_assessment_questions(response)
        if not assessment_questions:
            console.print("[bold red]Something went wrong while fetching assessment questions![/bold red]\n")
            return

        for idx, question_data in enumerate(assessment_questions, start=1):
            console.print(
                Panel(
                    question_data.get("question", ""),
                    title=f"[bold yellow]Question {idx}[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )

            learner_answer = Prompt.ask("[bold cyan]Enter your answer[/bold cyan]").strip()
            question_data["answer"] = learner_answer

        evaluation_response = self.ai_service.evaluate_assessment(
            assessment_questions,
            learner.learner_id,
        )

        console.print("\n[bold cyan]🤖 Evaluator[/bold cyan]")
        self._display_agent_response(evaluation_response)

    def _handle_chat(self, learner: object) -> None:
        user_prompt = self._request_user_prompt()
        if user_prompt is None:
            return

        with console.status("[bold magenta]🧠 AI Coach is thinking...[/bold magenta]", spinner="dots"):
            response = self.ai_service.chat(user_prompt, learner.learner_id)

        console.print("\n[bold cyan]🤖 AI Coach:[/bold cyan]")
        self._display_agent_response(response)

    def _exit_application(self) -> None:
        console.print(
            Panel(
                "[bold green]🙏 Thank you for using Agentic Pathshala![/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        sys.exit(0)

    def run(self, learner: object) -> None:
        while True:
            self.menu_handler.display_menu()
            choice = self.menu_handler.prompt_choice()
            if not choice:
                continue

            try:
                if choice == "1":
                    console.print("\n[bold blue]📂 Fetching assignments...[/bold blue]\n")
                    self.assignment_handler.view_assigned_assignments(learner.learner_id)
                elif choice == "2":
                    self.assignment_handler.view_available_assignments(learner.learner_id)
                elif choice == "3":
                    self._handle_assessment(learner)
                elif choice == "4":
                    self._handle_chat(learner)
                elif choice == "5":
                    self._exit_application()
                else:
                    console.print("[bold red]❌ Invalid option selected.[/bold red]\n")
            except Exception:
                logger.exception("Unexpected error during menu execution")
                console.print("[bold red]An unexpected error occurred. Please try again.[/bold red]\n")


if __name__ == "__main__":
    app = MainApp()
    app.login()