from typing import List, Optional
from models.learner import Learner
from utils.excel_store import read_records, write_record, update_record, delete_record, get_record

class LearnerRepository:
    def __init__(self) -> None:
        self.filename = "learners.xlsx"

    def _to_learner(self, record: dict) -> Learner:
        return Learner(
            learner_id=str(record.get("learner_id", "")).strip(),
            name=str(record.get("name", "")).strip(),
            email=str(record.get("email", "")).strip(),
            password=str(record.get("password", "")).strip(),
            assigned_coach_id=str(record.get("assigned_coach_id", "")).strip() if record.get("assigned_coach_id") else None,
            cohort_group=str(record.get("cohort_group", "")).strip() if record.get("cohort_group") else None,
        )

    def all(self) -> List[Learner]:
        records = read_records(self.filename)
        return [self._to_learner(record) for record in records]
        
    def get(self, learner_id: str) -> Optional[Learner]:
        record = get_record(self.filename, "learner_id", learner_id)
        if record:
            return self._to_learner(record)
        return None

    def find_by_credentials(self, email: str, password: str) -> Optional[Learner]:
        email = email.strip()
        password = password.strip()
        for learner in self.all():
            if learner.email == email and learner.password == password:
                return learner
        return None
        
    def create(self, learner: Learner) -> None:
        record = {
            "learner_id": learner.learner_id,
            "name": learner.name,
            "email": learner.email,
            "password": learner.password,
            "assigned_coach_id": learner.assigned_coach_id,
            "cohort_group": learner.cohort_group
        }
        write_record(self.filename, record)

    def update(self, learner_id: str, updates: dict) -> bool:
        return update_record(self.filename, "learner_id", learner_id, updates)

    def delete(self, learner_id: str) -> bool:
        return delete_record(self.filename, "learner_id", learner_id)
