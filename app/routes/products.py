from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/products")

@router.get("/")
def get_products(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return []

@router.post("/create")
def create_product(nom: str, prix_unitaire: float, current_user = Depends(get_current_user)):
    return {"message": "Module produits en cours de développement"}
