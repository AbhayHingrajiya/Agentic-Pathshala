
from mcp_server.server import get_assignments


class AssignmentHandler:

    def __init__(self):
        # Sample assignment database
        self.assignments = get_assignments().get("assignments", [])
        
    def view_assigned_assignments(self,learner_id):
        """Display assignments for the learner"""
        self.learner_id = learner_id
        self.filtered_assignments = [
            assignment
            for assignment in self.assignments
            if assignment["learner_id"] == self.learner_id
        ]
        print("\nYour Assignments:")
        for assignment in self.filtered_assignments:
            print(f"- {assignment['assignment_id']} : {assignment['status']}")
            
    def view_available_assignments(self,learner_id):
        """Display assignments for the learner"""
        self.learner_id = learner_id
        self.filtered_assignments = [
            assignment
            for assignment in self.assignments
            if assignment["learner_id"] != self.learner_id
        ]
        print("\nYour Assignments:")
        for assignment in self.filtered_assignments:
            print(f"- {assignment['assignment_id']} : {assignment['status']}")