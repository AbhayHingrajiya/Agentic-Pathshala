from dataclasses import dataclass
from typing import Optional

@dataclass
class LearnerAssignment:
    mapping_id: str
    learner_id: str
    assignment_id: str
    assigned_by_coach_id: str
    status: str
    progress_percentage: int
    assigned_date: Optional[str] = None
    completed_date: Optional[str] = None
