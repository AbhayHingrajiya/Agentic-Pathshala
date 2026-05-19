import sys
from pathlib import Path
from datetime import datetime
import uuid

# Ensure project root is on sys.path so utils, config, etc. are importable
# regardless of how the server is launched (direct file or -m module).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp import FastMCP
from repositories.learner_repository import LearnerRepository
from repositories.assignment_repository import AssignmentRepository
from repositories.learner_assignment_repository import LearnerAssignmentRepository
from models.learner_assignment import LearnerAssignment
from utils.excel_store import read_records


mcp = FastMCP(
    name="AI Learning Coach MCP Server"
)

learner_repo = LearnerRepository()
assignment_repo = AssignmentRepository()
learner_assignment_repo = LearnerAssignmentRepository()


@mcp.tool()
def ping() -> dict:
    return {
        "status": "working"
    }


@mcp.tool()
def get_learners() -> dict:
    learners = learner_repo.all()
    return {
        "count": len(learners),
        "learners": [
            {
                "learner_id": l.learner_id,
                "name": l.name,
                "email": l.email,
                "cohort_group": l.cohort_group
            } for l in learners
        ]
    }


@mcp.tool()
def get_assignments() -> dict:
    assignments = assignment_repo.all()
    return {
        "count": len(assignments),
        "assignments": [
            {
                "assignment_id": a.assignment_id,
                "title": a.title,
                "difficulty_level": a.difficulty_level
            } for a in assignments
        ]
    }


@mcp.tool()
def get_assignments_for_learner(learner_id: str) -> dict:
    """Get all assignments for a specific learner."""
    mappings = learner_assignment_repo.get_by_learner(learner_id)
    return {
        "learner_id": learner_id,
        "count": len(mappings),
        "assignments": [
            {
                "assignment_id": m.assignment_id,
                "status": m.status,
                "progress_percentage": m.progress_percentage
            } for m in mappings
        ]
    }

@mcp.tool()
def get_progress_for_learner(learner_id: str) -> dict:
    """Get all progress/score records for a specific learner."""
    all_progress = read_records("progress.xlsx")
    learner_progress = [
        p for p in all_progress
        if str(p.get("learner_id", "")).strip() == str(learner_id).strip()
    ]
    return {
        "learner_id": learner_id,
        "count": len(learner_progress),
        "progress": learner_progress
    }



@mcp.tool()
def validate_assignment_exists(assignment_id: str) -> dict:
    """Check if an assignment exists in the master catalog."""
    assignment = assignment_repo.get(assignment_id)
    if assignment:
        return {"exists": True, "title": assignment.title}
    return {"exists": False, "error": f"Assignment {assignment_id} not found."}


@mcp.tool()
def assign_task_to_learner(learner_id: str, assignment_id: str, coach_id: str) -> dict:
    """Assign a task to a learner if it hasn't been assigned yet."""
    # 1. Validate Assignment
    if not assignment_repo.get(assignment_id):
        return {"success": False, "error": f"Assignment {assignment_id} does not exist."}
    
    # 2. Validate Learner
    if not learner_repo.get(learner_id):
        return {"success": False, "error": f"Learner {learner_id} does not exist."}
        
    # 3. Check for existing mapping
    existing = learner_assignment_repo.get_by_learner(learner_id)
    for m in existing:
        if m.assignment_id == assignment_id:
            return {"success": False, "error": f"Task {assignment_id} is already assigned to {learner_id}."}
            
    # 4. Create Mapping
    mapping_id = f"M-{uuid.uuid4().hex[:6].upper()}"
    new_mapping = LearnerAssignment(
        mapping_id=mapping_id,
        learner_id=learner_id,
        assignment_id=assignment_id,
        assigned_by_coach_id=coach_id,
        status="Pending",
        progress_percentage=0,
        assigned_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    learner_assignment_repo.create(new_mapping)
    
    return {
        "success": True, 
        "mapping_id": mapping_id, 
        "message": f"Successfully assigned {assignment_id} to {learner_id}"
    }


@mcp.tool()
def remove_task_from_learner(learner_id: str, assignment_id: str) -> dict:
    """Remove / de-assign a task from a learner."""
    mappings = learner_assignment_repo.get_by_learner(learner_id)
    target_mapping = None
    for m in mappings:
        if m.assignment_id == assignment_id:
            target_mapping = m
            break
            
    if not target_mapping:
        return {"success": False, "error": f"Assignment {assignment_id} is not assigned to {learner_id}."}
        
    success = learner_assignment_repo.delete(target_mapping.mapping_id)
    if success:
        return {"success": True, "message": f"Successfully removed {assignment_id} from {learner_id}"}
    return {"success": False, "error": "Failed to delete database record."}

@mcp.tool()
def update_learner_assignment_progress(
    learner_id: str,
    assignment_id: str,
    progress_percentage: int,
    status: str = "completed"
) -> dict:
    """Update a learner's assignment status and progress percentage after assessment."""
    mappings = learner_assignment_repo.get_by_learner(learner_id)
    target = None
    for m in mappings:
        if m.assignment_id.strip().lower() == assignment_id.strip().lower():
            target = m
            break
    if not target:
        return {
            "success": False,
            "error": f"Assignment '{assignment_id}' is not assigned to learner '{learner_id}'."
        }
    success = learner_assignment_repo.update(
        target.mapping_id,
        {"status": status, "progress_percentage": progress_percentage, "completed_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )
    if success:
        return {
            "success": True,
            "message": f"Updated '{assignment_id}' for '{learner_id}': status={status}, score={progress_percentage}%"
        }
    return {"success": False, "error": "Failed to update record in storage."}

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )