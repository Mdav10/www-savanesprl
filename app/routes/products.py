from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User, ActiviteLog
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
            "prix_unitaire": p.prix_unitaire,
            "created_at": p.created_at
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
    product = Product(
        nom=nom,
        prix_unitaire=prix_unitaire,
        created_by=current_user.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {"message": "Produit créé", "product_id": product.id}

@router.put("/{product_id}")
def update_product(
    product_id: int,
    nom: str = None,
    prix_unitaire: float = None,
    current_user = Depends(role_required(["DG", "DIRECTEUR_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    if nom:
        product.nom = nom
    if prix_unitaire:
        product.prix_unitaire = prix_unitaire
    
    db.commit()
    
    return {"message": "Produit modifié"}
