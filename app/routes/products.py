from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/")
def get_products(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    products = db.query(Product).order_by(Product.nom).all()
    return [
        {
            "id": p.id,
            "nom": p.nom,
            "prix_unitaire": p.prix_unitaire
        }
        for p in products
    ]

@router.post("/create")
def create_product(
    nom: str,
    prix_unitaire: float,
    current_user = Depends(role_required(["DG", "DIRECTEUR_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    if prix_unitaire <= 0:
        raise HTTPException(status_code=400, detail="Le prix doit être positif")
    
    product = Product(
        nom=nom,
        prix_unitaire=prix_unitaire
    )
    db.add(product)
    db.commit()
    
    return {"message": "Produit créé", "product_id": product.id}
