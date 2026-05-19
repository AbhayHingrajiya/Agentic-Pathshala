from dataclasses import dataclass
from typing import Optional

@dataclass
class Learner:
    learner_id: str
    name: str
    email: str
    password: str
    assigned_coach_id: Optional[str] = None
    cohort_group: Optional[str] = None
