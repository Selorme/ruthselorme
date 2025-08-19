# test_db.py
from app import app
from models import Base
from extensions import db
from jobs_skills_database import create_skills_database, create_jobs_database

with app.app_context():
    print("Creating tables...")
    Base.metadata.create_all(bind=db.engine)

    # Check what was created
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")


    # 2. Check if data already exists (to avoid duplicates)
    from models import SkillsReference, Job

    # 3. Add skills data if empty
    if db.session.query(SkillsReference).count() == 0:
        print("Adding skills data...")
        create_skills_database()

    # 4. Add jobs data if empty
    if db.session.query(Job).count() == 0:
        print("Adding jobs data...")
        create_jobs_database()