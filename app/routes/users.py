from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user, role_required
from app.utils import get_password_hash

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/")
def get_all_users(
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "nom": u.nom,
            "username": u.username,
            "email": u.email,
            "role": u.role_id,
            "is_active": u.is_active
        }
        for u in users
    ]

@router.post("/create")
def create_user(
    nom: str,
    email: str,
    username: str,
    mot_de_passe: str,
    role: str,
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    # Check if username already exists (only username must be unique)
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
    
    # Validate role
    valid_roles = ["DT", "DAF", "DIRECTEUR_COMMERCIAL", "COMPTABLE", "AGENT_STOCK", "AGENT_COMMERCIAL"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    # Validate password length
    if len(mot_de_passe) < 4:
        raise HTTPException(status_code=400, detail="Le mot de passe doit avoir au moins 4 caractères")
    
    # Create user (email can be duplicate - no check)
    hashed = get_password_hash(mot_de_passe)
    new_user = User(
        nom=nom,
        email=email,
        username=username,
        mot_de_passe=hashed,
        role_id=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Utilisateur créé avec succès", "user_id": new_user.id, "username": username}
