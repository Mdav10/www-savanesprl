from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils import verify_password, get_password_hash, create_token
import os

router = APIRouter(prefix="/api/auth")

DG_USERNAME = "OsiasHab"
DG_PASSWORD = "08800Osi"

def init_dg(db: Session):
    user = db.query(User).filter(User.username == DG_USERNAME).first()
    if not user:
        new_user = User(
            nom="Directeur General",
            email="dg@savane.com",
            username=DG_USERNAME,
            mot_de_passe=get_password_hash(DG_PASSWORD),
            role="DG",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print("✅ DG created")
    elif user.role is None:
        user.role = "DG"
        db.commit()
        print("✅ DG role fixed")

@router.post("/login")
def login(username: str, mot_de_passe: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Compte désactivé")
    
    return {
        "access_token": create_token({"user_id": user.id, "role": user.role}),
        "role": user.role,
        "nom": user.nom
    }
