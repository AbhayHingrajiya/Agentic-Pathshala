from typing import List

from mcp_server.server import get_assignments
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
        return [assignment for assignment in self._assignments if assignment.learner_id == learner_id]

    def get_available(self, learner_id: str) -> List[Assignment]:
        learner_id = str(learner_id).strip()
        return [assignment for assignment in self._assignments if assignment.learner_id != learner_id]
