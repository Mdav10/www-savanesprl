from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ActiviteLog, RoleEnum
from app.utils import verify_password, get_password_hash, create_access_token
from app.schemas import UserLogin, TokenResponse
from app.auth import get_current_user, role_required
import os

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

DG_USERNAME = os.getenv("DG_USERNAME", "OsiasHab")
DG_PASSWORD = os.getenv("DG_PASSWORD", "08800Osi")

def create_default_dg(db: Session):
    dg_user = db.query(User).filter(User.username == DG_USERNAME).first()
    if not dg_user:
        hashed_password = get_password_hash(DG_PASSWORD)
        dg = User(
            nom="Directeur General",
            email="dg@savanesprl.com",
            username=DG_USERNAME,
            mot_de_passe=hashed_password,
            role_id=RoleEnum.DG,
            is_active=True
        )
        db.add(dg)
        db.commit()
        print("✅ DG created")
    else:
        print("✅ DG exists")

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Compte désactivé")
    
    token = create_access_token({"user_id": user.id, "role": user.role_id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nom": user.nom,
        "role": user.role_id
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"message": "Déconnecté"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nom": current_user.nom,
        "role": current_user.role_id,
        "is_active": current_user.is_active
    }
