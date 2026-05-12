from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils import decode_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé ou désactivé")
    
    return user

def role_required(allowed_roles):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role_id not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail="Permission refusée"
            )
        return current_user
    return role_checker
