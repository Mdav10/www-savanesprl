from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ActiviteLog, RoleEnum
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
    existing = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ou nom d'utilisateur déjà utilisé")
    
    if role not in [r.value for r in RoleEnum]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    hashed = get_password_hash(mot_de_passe)
    new_user = User(
        nom=nom,
        email=email,
        username=username,
        mot_de_passe=hashed,
        role_id=role
    )
    db.add(new_user)
    db.commit()
    
    return {"message": "Utilisateur créé", "user_id": new_user.id}

@router.post("/disable/{user_id}")
def disable_user(
    user_id: int,
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de se désactiver soi-même")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.is_active = False
    db.commit()
    
    return {"message": f"Utilisateur {user.nom} désactivé"}

@router.post("/enable/{user_id}")
def enable_user(
    user_id: int,
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.is_active = True
    db.commit()
    
    return {"message": f"Utilisateur {user.nom} réactivé"}
