from utils.excel_store import write_record


def seed_learners():

    learners = [
        {
            "learner_id": "L001",
            "name": "Alice"
        },
        {
            "learner_id": "L002",
            "name": "Bob"
        },
        {
            "learner_id": "L003",
            "name": "Charlie"
        }
    ]

    for learner in learners:
        write_record("learners.xlsx", learner)


def seed_assignments():

    assignments = [
        {
            "learner_id": "L001",
            "assignment_id": "week1_python",
            "status": "submitted"
        },
        {
            "learner_id": "L002",
            "assignment_id": "week1_python",
            "status": "pending"
        }
    ]

    for assignment in assignments:
        write_record("assignments.xlsx", assignment)


def seed_progress():

    progress = [
        {
            "learner_id": "L001",
            "topic": "Python Basics",
            "score": 85
        },
        {
            "learner_id": "L002",
            "topic": "Python Basics",
            "score": 60
        }
    ]

    for item in progress:
        write_record("progress.xlsx", item)


def seed_notes():

    notes = [
        {
            "learner_id": "L001",
            "topic": "RAG",
            "content": "ChromaDB stores embeddings"
        }
    ]

    for note in notes:
        write_record("notes.xlsx", note)


if __name__ == "__main__":

    seed_learners()
    seed_assignments()
    seed_progress()
    seed_notes()

    print("Storage seeded successfully.")