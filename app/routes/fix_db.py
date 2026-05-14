from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database import engine
from app.auth import get_current_user

router = APIRouter(prefix="/api/fix", tags=["fix"])

@router.get("/database")
def fix_database(current_user = Depends(get_current_user)):
    if current_user.role != "DG":
        return {"error": "Seul le DG peut faire cette action"}
    
    results = []
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        
        # Remove unique constraint from email
        try:
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key"))
            conn.execute(text("DROP INDEX IF EXISTS ix_users_email"))
            results.append("✅ Contrainte email unique supprimée")
        except Exception as e:
            results.append(f"Note email: {e}")
        
        # Add missing enum values
        for val in ['AGENT_STOCK', 'AGENT_COMMERCIAL', 'DIRECTEUR_COMMERCIAL']:
            try:
                conn.execute(text(f"ALTER TYPE roleenum ADD VALUE IF NOT EXISTS '{val}'"))
                results.append(f"✅ {val} ajouté")
            except Exception as e:
                results.append(f"Note {val}: {e}")
        
        conn.commit()
    
    return {"message": "Base de données corrigée", "details": results}
