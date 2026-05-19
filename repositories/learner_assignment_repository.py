from typing import List, Optional
from models.learner_assignment import LearnerAssignment
from utils.excel_store import read_records, write_record, update_record, delete_record, get_record

class LearnerAssignmentRepository:
    def __init__(self) -> None:
        self.filename = "learner_assignments.xlsx"

    def _to_mapping(self, record: dict) -> LearnerAssignment:
        return LearnerAssignment(
            mapping_id=str(record.get("mapping_id", "")).strip(),
            learner_id=str(record.get("learner_id", "")).strip(),
            assignment_id=str(record.get("assignment_id", "")).strip(),
            assigned_by_coach_id=str(record.get("assigned_by_coach_id", "")).strip(),
            status=str(record.get("status", "")).strip(),
            progress_percentage=int(float(str(record.get("progress_percentage", "0")))) if record.get("progress_percentage") else 0,
            assigned_date=str(record.get("assigned_date", "")).strip() if record.get("assigned_date") else None,
            completed_date=str(record.get("completed_date", "")).strip() if record.get("completed_date") else None,
        )

    def all(self) -> List[LearnerAssignment]:
        records = read_records(self.filename)
        return [self._to_mapping(record) for record in records]

    def get_by_learner(self, learner_id: str) -> List[LearnerAssignment]:
        return [m for m in self.all() if m.learner_id == learner_id]

    def get_by_assignment(self, assignment_id: str) -> List[LearnerAssignment]:
        return [m for m in self.all() if m.assignment_id == assignment_id]

    def create(self, mapping: LearnerAssignment) -> None:
        record = {
            "mapping_id": mapping.mapping_id,
            "learner_id": mapping.learner_id,
            "assignment_id": mapping.assignment_id,
            "assigned_by_coach_id": mapping.assigned_by_coach_id,
            "status": mapping.status,
            "progress_percentage": mapping.progress_percentage,
            "assigned_date": mapping.assigned_date,
            "completed_date": mapping.completed_date
        }
        write_record(self.filename, record)

    def update(self, mapping_id: str, updates: dict) -> bool:
        return update_record(self.filename, "mapping_id", mapping_id, updates)

    def delete(self, mapping_id: str) -> bool:
        return delete_record(self.filename, "mapping_id", mapping_id)
