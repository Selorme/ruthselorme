# create_tables.py - Run this script to create the missing tables

from extensions import db
from models import Base, SkillsReference, UserSkill, Job, JobMatch
from app import app  # Replace 'your_app' with your actual app file name


def create_tables():
    """Create all tables defined in models"""
    with app.app_context():
        try:
            # Method 1: Using Base metadata (recommended for SQLAlchemy 2.0)
            Base.metadata.create_all(bind=db.engine)
            print("✅ All tables created successfully using Base.metadata.create_all()")

            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            expected_tables = ['skills_reference', 'user_skills', 'jobs', 'job_matches']

            print("\n📋 Table creation status:")
            for table in expected_tables:
                if table in tables:
                    print(f"✅ {table} - EXISTS")
                else:
                    print(f"❌ {table} - MISSING")

        except Exception as e:
            print(f"❌ Error creating tables: {e}")


if __name__ == "__main__":
    create_tables()