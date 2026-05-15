from typing import List

from models.assignment import Assignment
from repositories.assignment_repository import AssignmentRepository


class AssignmentService:
    def __init__(self, repository: AssignmentRepository) -> None:
        self._repository = repository

    def get_assigned_assignments(self, learner_id: str) -> List[Assignment]:
        return self._repository.get_assigned(learner_id)

    def get_available_assignments(self, learner_id: str) -> List[Assignment]:
        return self._repository.get_available(learner_id)
