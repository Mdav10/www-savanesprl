from sqlalchemy import text
from app.database import engine

def fix_database():
    """Fix database schema - add role column if missing"""
    with engine.connect() as conn:
        # Check if role column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='role'
        """))
        
        if result.fetchone() is None:
            print("Adding role column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR"))
            conn.commit()
            print("✅ Role column added")
            
            # Update existing DG user
            conn.execute(text("UPDATE users SET role = 'DG' WHERE username = 'OsiasHab'"))
            conn.commit()
            print("✅ DG role updated")
        else:
            print("✅ Role column already exists")
