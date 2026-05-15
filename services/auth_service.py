from typing import Optional

from models.learner import Learner
from repositories.learner_repository import LearnerRepository


class AuthService:
    def __init__(self, learner_repository: LearnerRepository) -> None:
        self._repository = learner_repository

    def authenticate(self, email: str, password: str) -> Optional[Learner]:
        if not email or not password:
            return None
        return self._repository.find_by_credentials(email, password)
