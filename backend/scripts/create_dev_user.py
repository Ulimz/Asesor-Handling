
import sys
import os

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User

def create_user():
    db = SessionLocal()
    email = "admin@aeros.com"
    password = "password123"
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists.")
            # Update password just in case
            user.hashed_password = password
            db.commit()
            print("Password reset to 'password123'")
        else:
            new_user = User(
                email=email,
                full_name="Admin Dev",
                hashed_password=password, # Note: using plain text as per current implementation
                is_active=True
            )
            db.add(new_user)
            db.commit()
            print(f"User {email} created successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
