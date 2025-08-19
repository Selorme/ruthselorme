# fix_migration.py
from app import app, db  # Import your Flask app and db
from models import PasswordResetToken

with app.app_context():
    # Update all existing tokens to have is_used = False
    db.session.query(PasswordResetToken).filter(
        PasswordResetToken.is_used == None
    ).update({'is_used': False})
    db.session.commit()
    print("Fixed existing password reset tokens!")