from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils import verify_password, get_password_hash, create_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth")

class LoginRequest(BaseModel):
    username: str
    mot_de_passe: str

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
            role_id="DG",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print("✅ DG created")
    elif user.role_id is None:
        user.role_id = "DG"
        db.commit()
        print("✅ DG role fixed")

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Compte désactivé")
    
    token = create_token({"user_id": user.id, "role": user.role_id})
    
    return {
        "access_token": token,
        "role": user.role_id,
        "nom": user.nom
    }
