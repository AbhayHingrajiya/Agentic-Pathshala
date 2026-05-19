from dataclasses import dataclass
from typing import Optional

@dataclass
class Assignment:
    assignment_id: str
    title: str
    description: str
    difficulty_level: str
    creation_date: Optional[str] = None
