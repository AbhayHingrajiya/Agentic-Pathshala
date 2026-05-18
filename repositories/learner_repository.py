from typing import List, Optional

from mcp_server.server import get_learners
from models.learner import Learner


class LearnerRepository:
    def __init__(self) -> None:
        self._learners = [self._to_learner(record) for record in get_learners().get("learners", [])]

    @staticmethod
    def _to_learner(record: dict) -> Learner:
        return Learner(
            learner_id=str(record.get("learner_id", "")).strip(),
            name=str(record.get("name", "")).strip(),
            email=str(record.get("email", "")).strip(),
            password=str(record.get("password", "")).strip(),
        )

    def all(self) -> List[Learner]:
        return list(self._learners)

    def find_by_credentials(self, email: str, password: str) -> Optional[Learner]:
        email = email.strip()
        password = password.strip()
        for learner in self._learners:
            if learner.email == email and learner.password == password:
                return learner
        return None
