from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from models.learner import Learner
from services.auth_service import AuthService


class LoginHandler:
    def __init__(self, auth_service: AuthService, console: Console) -> None:
        self._auth_service = auth_service
        self._console = console

    def login(self) -> Optional[Learner]:
        self._console.print(
            Panel.fit("[bold cyan]AI Learning Coach Login[/bold cyan]", border_style="cyan")
        )

        email = Prompt.ask("Enter Email", default="bhavesh.gediya@azilen.com").strip()
        password = Prompt.ask("Enter Password", password=True, default="bhavesh@123").strip()

        learner = self._auth_service.authenticate(email, password)
        if not learner:
            self._console.print(
                Panel(
                    "[bold red]Invalid email or password[/bold red]",
                    title="Authentication Failed",
                    border_style="red",
                )
            )
            return None

        self._console.print(
            Panel(
                f"[bold green]Login Successful[/bold green]\n\nLearner ID : {learner.learner_id}\nName       : {learner.name}\nEmail      : {learner.email}",
                title="Welcome",
                border_style="green",
            )
        )
        return learner
