from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/fix", tags=["fix"])

@router.post("/update-roles")
def update_user_roles(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "DG":
        return {"error": "Unauthorized"}
    
    # Map usernames to roles based on what they should be
    role_map = {
        "Dt": "DT",
        "Agent": "AGENT_STOCK",
        "Daf": "DAF",
        "Emile": "AGENT_COMMERCIAL",
        "Comptable": "COMPTABLE",
        "Alexis": "DAF",
        "Coyi": "DIRECTEUR_COMMERCIAL",
        "Osi": "AGENT_COMMERCIAL",
        "Bbb": "AGENT_STOCK",
        "Commerce": "AGENT_COMMERCIAL"
    }
    
    updated = 0
    for username, correct_role in role_map.items():
        user = db.query(User).filter(User.username == username).first()
        if user and (user.role is None or user.role == "null"):
            user.role = correct_role
            updated += 1
    
    db.commit()
    return {"message": f"Updated {updated} users with correct roles"}
