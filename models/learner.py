from dataclasses import dataclass


@dataclass
class Learner:
    learner_id: str
    name: str
    email: str
    password: str
