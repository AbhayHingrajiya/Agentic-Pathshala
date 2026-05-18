from typing import Iterable

from rich.console import Console
from rich.table import Table
from rich import box

from models.assignment import Assignment
from services.assignment_service import AssignmentService


class AssignmentHandler:
    def __init__(self, assignment_service: AssignmentService, console: Console) -> None:
        self._service = assignment_service
        self._console = console

    def _render_assignments(self, assignments: Iterable[Assignment], title: str) -> None:
        if not assignments:
            self._console.print(f"[bold yellow]No {title.lower()} found[/bold yellow]\n")
            return

        table = Table(title=title, box=box.ROUNDED, border_style="cyan", show_lines=True)
        table.add_column("Assignment ID", style="bold green")
        table.add_column("Status", style="bold white")

        for assignment in assignments:
            table.add_row(assignment.assignment_id, assignment.status)

        self._console.print(table)

    def view_assigned_assignments(self, learner_id: str) -> None:
        assignments = self._service.get_assigned_assignments(learner_id)
        self._render_assignments(assignments, "Assigned Assignments")

    def view_available_assignments(self, learner_id: str) -> None:
        assignments = self._service.get_available_assignments(learner_id)
        self._render_assignments(assignments, "Available Assignments")
