from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from models.user_session import UserSession
from services.auth_service import AuthService

class LoginHandler:
    def __init__(self, auth_service: AuthService, console: Console) -> None:
        self._auth_service = auth_service
        self._console = console

    def login(self) -> Optional[UserSession]:
        self._console.print(
            Panel.fit("[bold cyan]AI Learning Coach Login[/bold cyan]", border_style="cyan")
        )

        email = Prompt.ask("Enter Email", default="bhavesh.gediya@azilen.com").strip()
        password = Prompt.ask("Enter Password", password=True, default="bhavesh@123").strip()

        session = self._auth_service.authenticate(email, password)
        if not session:
            self._console.print(
                Panel(
                    "[bold red]Invalid email or password[/bold red]",
                    title="Authentication Failed",
                    border_style="red",
                )
            )
            return None

        role_color = "magenta" if session.role == "coach" else "green"
        self._console.print(
            Panel(
                f"[bold green]Login Successful[/bold green]\n\nRole       : [{role_color}]{session.role.upper()}[/{role_color}]\nUser ID    : {session.user_id}\nName       : {session.name}\nEmail      : {session.email}",
                title="Welcome",
                border_style="green",
            )
        )
        return session
