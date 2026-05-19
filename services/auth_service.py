from typing import Optional
from models.user_session import UserSession
from repositories.learner_repository import LearnerRepository
from repositories.coach_repository import CoachRepository

class AuthService:
    def __init__(self, learner_repository: LearnerRepository, coach_repository: CoachRepository) -> None:
        self._learner_repository = learner_repository
        self._coach_repository = coach_repository

    def authenticate(self, email: str, password: str) -> Optional[UserSession]:
        if not email or not password:
            return None
        
        # 1. Check if it's a Coach (simple email match for prototype)
        for coach in self._coach_repository.all():
            if coach.email == email:
                return UserSession(
                    user_id=coach.coach_id,
                    name=coach.name,
                    email=coach.email,
                    role="coach"
                )

        # 2. Check if it's a Learner
        learner = self._learner_repository.find_by_credentials(email, password)
        if learner:
            return UserSession(
                user_id=learner.learner_id,
                name=learner.name,
                email=learner.email,
                role="learner"
            )

        return None
