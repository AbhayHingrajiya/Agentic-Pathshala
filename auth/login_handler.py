from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from UI.menu_handler import MenuHandler
from mcp_server.server import get_learners

console = Console()

class LoginHandler:
    def __init__(self):
        # Initialize handlers
        self.menu_handler = MenuHandler()
        
        # Sample learner database
        self.learners = get_learners().get("learners", [])


    def login(self):
        console.print(
            Panel.fit(
                "[bold cyan]AI Learning Coach Login[/bold cyan]",
                border_style="cyan"
            )
        )

        email = Prompt.ask("Enter Email", default="bhavesh.gediya@azilen.com").strip()
        password = Prompt.ask("Enter Password", password=True, default="bhavesh@123").strip()

        for learner in self.learners:
            if learner["email"] == email and learner["password"] == password:

                console.print(
                    Panel(
                        f"""
    [bold green]Login Successful[/bold green]

    Learner ID : {learner['learner_id']}
    Name       : {learner['name']}
    Email      : {learner['email']}
                        """,
                        title="Welcome",
                        border_style="green"
                    )
                )

                return learner

        console.print(
            Panel(
                "[bold red]Invalid email or password[/bold red]",
                title="Authentication Failed",
                border_style="red"
            )
        )

        return None


# if __name__ == "__main__":
#     login()