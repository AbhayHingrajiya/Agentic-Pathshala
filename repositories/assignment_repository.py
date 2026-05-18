from typing import List

from mcp_server.server import get_assignments, get_assignments_for_learner
from models.assignment import Assignment


class AssignmentRepository:
    def __init__(self) -> None:
        self._assignments = [self._to_assignment(record) for record in get_assignments().get("assignments", [])]

    @staticmethod
    def _to_assignment(record: dict) -> Assignment:
        return Assignment(
            assignment_id=str(record.get("assignment_id", "")).strip(),
            learner_id=str(record.get("learner_id", "")).strip(),
            status=str(record.get("status", "")).strip(),
        )

    def all(self) -> List[Assignment]:
        return list(self._assignments)

    def get_assigned(self, learner_id: str) -> List[Assignment]:
        learner_id = str(learner_id).strip()
        return [self._to_assignment(record) for record in get_assignments_for_learner(learner_id).get("assignments", [])]

    def get_available(self, learner_id: str) -> List[Assignment]:
        learner_id = str(learner_id).strip()
        # Assigned assignments for learner
        assigned_assignments = [
            self._to_assignment(record)
            for record in get_assignments_for_learner(learner_id).get("assignments", [])
        ]

        # All available assignments
        available_assignments = [
            self._to_assignment(record)
            for record in get_assignments().get("assignments", [])
        ]

        # Remove already assigned assignments from available assignments
        assigned_ids = {
            assignment.assignment_id
            for assignment in assigned_assignments
        }

        learner_available_assignments = [
            assignment
            for assignment in available_assignments
            if assignment.assignment_id not in assigned_ids
        ]
        return learner_available_assignments
