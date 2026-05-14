from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.auth import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/")
def get_products(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [{"id": p.id, "nom": p.nom, "prix_unitaire": p.prix_unitaire} for p in products]

@router.post("/create")
def create_product(
    nom: str,
    prix_unitaire: float,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role_id not in ["DG", "DIRECTEUR_COMMERCIAL"]:
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    new_product = Product(
        nom=nom,
        prix_unitaire=prix_unitaire
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {"message": "Produit créé", "product": {"id": new_product.id, "nom": new_product.nom, "prix_unitaire": new_product.prix_unitaire}}
