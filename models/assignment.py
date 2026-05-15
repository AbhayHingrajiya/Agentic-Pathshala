from dataclasses import dataclass


@dataclass
class Assignment:
    assignment_id: str
    learner_id: str
    status: str
