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

def init_dg(db: Session):
    if not db.query(User).filter(User.username == "OsiasHab").first():
        db.add(User(
            nom="Directeur General",
            email="dg@savane.com",
            username="OsiasHab",
            mot_de_passe=get_password_hash("08800Osi"),
            role="DG",
            is_active=True
        ))
        db.commit()
        print("✅ DG created")

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    return {
        "access_token": create_token({"user_id": user.id, "role": user.role}),
        "role": user.role,
        "nom": user.nom
    }
