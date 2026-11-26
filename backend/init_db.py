"""
Database initialization script for StudyMatch AI.
Creates all database tables defined in models.py and stamps Alembic head.
"""
from database import engine
from models import Base

def init_db():
    print("Creating all database tables in studymatch_db...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

    try:
        import alembic.config
        print("Stamping Alembic migration version to head...")
        alembic.config.main(argv=["stamp", "head"])
        print("Alembic migration version set to head successfully.")
    except Exception as e:
        print(f"Notice: Alembic stamp: {e}")

    try:
        from seed_day1 import seed_curriculum
        from seed_day2_questions import seed_questions
        from seed_diploma_computer_sem3 import seed_diploma_computer_sem3
        print("Seeding core academic subjects and diagnostic questions...")
        seed_curriculum()
        seed_questions()
        seed_diploma_computer_sem3()
        print("Core subjects and quizzes seeded successfully!")
    except Exception as e:
        print(f"Notice: Seeding curriculum: {e}")

if __name__ == "__main__":
    init_db()
