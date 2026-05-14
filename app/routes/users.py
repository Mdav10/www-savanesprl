from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.utils import get_password_hash

router = APIRouter(prefix="/api/users")

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
    if current_user.role != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    new_user = User(
        nom=nom,
        email=email,
        username=username,
        mot_de_passe=get_password_hash(mot_de_passe),
        role=role
    )
    db.add(new_user)
    db.commit()
    
    return {"message": "Utilisateur créé", "user": {"id": new_user.id, "nom": new_user.nom, "username": new_user.username, "role": new_user.role}}

@router.delete("/{user_id}")
def delete_user(user_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"Utilisateur {user.nom} supprimé"}

@router.delete("/delete-all")
def delete_all_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "DG":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    deleted = db.query(User).filter(User.id != current_user.id).delete()
    db.commit()
    
    return {"message": f"{deleted} utilisateurs supprimés"}
