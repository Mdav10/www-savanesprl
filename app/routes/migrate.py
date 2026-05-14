from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database import get_db, engine
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/migrate", tags=["Migration"])

@router.post("/fix-role-column")
def fix_role_column(current_user = Depends(role_required(["DG"])), db = Depends(get_db)):
    try:
        # Check if role column exists
        with engine.connect() as conn:
            # Add role column if it doesn't exist
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50)"))
                conn.commit()
            except Exception as e:
                print(f"Error adding column: {e}")
            
            # Update existing users to have a default role
            conn.execute(text("UPDATE users SET role = 'USER' WHERE role IS NULL"))
            conn.commit()
            
            # Update DG user
            conn.execute(text("UPDATE users SET role = 'DG' WHERE username = 'OsiasHab'"))
            conn.commit()
            
        return {"message": "✅ Database fixed successfully"}
    except Exception as e:
        return {"error": str(e)}
