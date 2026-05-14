from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.utils import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/")
def get_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    users = db.query(User).all()
    return [{"id": u.id, "nom": u.nom, "username": u.username, "email": u.email, "role": u.role} for u in users]

@router.post("/create")
def create_user(
    nom: str,
    email: str,
    username: str,
    mot_de_passe: str,
    role: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Creating user: {nom}, {email}, {username}, {role}")  # Debug log
    
    if current_user.role != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Check if username exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    # Create new user
    new_user = User(
        nom=nom,
        email=email,
        username=username,
        mot_de_passe=get_password_hash(mot_de_passe),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Utilisateur créé avec succès", "user": {"id": new_user.id, "nom": new_user.nom, "username": new_user.username, "role": new_user.role}}
