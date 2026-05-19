import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.coach import Coach
from repositories.coach_repository import CoachRepository

def seed():
    print("Seeding Coaches Database...")
    repo = CoachRepository()
    
    # Check if coach C001 already exists
    if repo.get("C001"):
        print("Coach C001 already exists. Skipping.")
        return
        
    coach = Coach(
        coach_id="C001",
        name="Lead AI Architect",
        email="coach@pathshala.com",
        department="Computer Science"
    )
    repo.create(coach)
    print("Successfully seeded coach@pathshala.com (C001) in coaches.xlsx!")

if __name__ == "__main__":
    seed()
