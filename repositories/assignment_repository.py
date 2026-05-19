from typing import List, Optional
from models.assignment import Assignment
from utils.excel_store import read_records, write_record, update_record, delete_record, get_record

class AssignmentRepository:
    def __init__(self) -> None:
        self.filename = "assignments.xlsx"

    def _to_assignment(self, record: dict) -> Assignment:
        return Assignment(
            assignment_id=str(record.get("assignment_id", "")).strip(),
            title=str(record.get("title", "")).strip(),
            description=str(record.get("description", "")).strip(),
            difficulty_level=str(record.get("difficulty_level", "")).strip(),
            creation_date=str(record.get("creation_date", "")).strip() if record.get("creation_date") else None,
        )

    def all(self) -> List[Assignment]:
        records = read_records(self.filename)
        return [self._to_assignment(record) for record in records]

    def get(self, assignment_id: str) -> Optional[Assignment]:
        record = get_record(self.filename, "assignment_id", assignment_id)
        if record:
            return self._to_assignment(record)
        return None

    def create(self, assignment: Assignment) -> None:
        record = {
            "assignment_id": assignment.assignment_id,
            "title": assignment.title,
            "description": assignment.description,
            "difficulty_level": assignment.difficulty_level,
            "creation_date": assignment.creation_date
        }
        write_record(self.filename, record)

    def update(self, assignment_id: str, updates: dict) -> bool:
        return update_record(self.filename, "assignment_id", assignment_id, updates)

    def delete(self, assignment_id: str) -> bool:
        return delete_record(self.filename, "assignment_id", assignment_id)
