from dataclasses import dataclass

@dataclass
class UserSession:
    user_id: str
    name: str
    email: str
    role: str
