from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.utils import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/")
def get_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    users = db.query(User).all()
    return [{"id": u.id, "nom": u.nom, "username": u.username, "email": u.email, "role": u.role_id} for u in users]

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
    try:
        print(f"Creating user: {nom}, {username}, role={role}")
        
        if current_user.role_id != "DG":
            raise HTTPException(status_code=403, detail="Permission refusée")
        
        if not nom or not email or not username or not mot_de_passe:
            raise HTTPException(status_code=400, detail="Tous les champs sont requis")
        
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
        
        hashed_password = get_password_hash(mot_de_passe)
        new_user = User(
            nom=nom,
            email=email,
            username=username,
            mot_de_passe=hashed_password,
            role_id=role,  # Using role_id column
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "Utilisateur créé avec succès", 
            "user": {
                "id": new_user.id, 
                "nom": new_user.nom, 
                "username": new_user.username, 
                "role": new_user.role_id
            }
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
