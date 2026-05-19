from typing import List, Optional
from models.coach import Coach
from utils.excel_store import read_records, write_record, update_record, delete_record, get_record

class CoachRepository:
    def __init__(self) -> None:
        self.filename = "coaches.xlsx"

    def _to_coach(self, record: dict) -> Coach:
        return Coach(
            coach_id=str(record.get("coach_id", "")).strip(),
            name=str(record.get("name", "")).strip(),
            email=str(record.get("email", "")).strip(),
            department=str(record.get("department", "")).strip(),
        )

    def all(self) -> List[Coach]:
        records = read_records(self.filename)
        return [self._to_coach(record) for record in records]

    def get(self, coach_id: str) -> Optional[Coach]:
        record = get_record(self.filename, "coach_id", coach_id)
        if record:
            return self._to_coach(record)
        return None

    def create(self, coach: Coach) -> None:
        record = {
            "coach_id": coach.coach_id,
            "name": coach.name,
            "email": coach.email,
            "department": coach.department
        }
        write_record(self.filename, record)

    def update(self, coach_id: str, updates: dict) -> bool:
        return update_record(self.filename, "coach_id", coach_id, updates)

    def delete(self, coach_id: str) -> bool:
        return delete_record(self.filename, "coach_id", coach_id)
