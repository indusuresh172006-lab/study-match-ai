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

if __name__ == "__main__":
    init_db()
