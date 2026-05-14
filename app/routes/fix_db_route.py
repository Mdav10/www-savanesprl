from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database import engine
from app.auth import get_current_user

router = APIRouter(prefix="/api/fix", tags=["fix"])

@router.get("/database")
def fix_database(current_user = Depends(get_current_user)):
    """Run this once to fix database constraints and enum values"""
    if current_user.role_id != "DG":
        return {"error": "Only DG can run this fix"}
    
    results = []
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        
        # Remove email unique constraint
        try:
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS ix_users_email"))
            results.append("✅ Email unique constraint removed")
        except Exception as e:
            results.append(f"Note: {e}")
        
        # Add enum values
        for val in ['AGENT_STOCK', 'AGENT_COMMERCIAL', 'DIRECTEUR_COMMERCIAL']:
            try:
                conn.execute(text(f"ALTER TYPE roleenum ADD VALUE IF NOT EXISTS '{val}'"))
                results.append(f"✅ {val} added to enum")
            except Exception as e:
                results.append(f"Note for {val}: {e}")
        
        conn.commit()
    
    return {"message": "Database fixed", "details": results}
