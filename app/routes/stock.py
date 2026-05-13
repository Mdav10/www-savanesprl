from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models import StockMovement, Product, User, ActiviteLog
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/stock", tags=["Stock"])

@router.post("/movement")
def create_stock_movement(
    product_id: int,
    quantite_entree: int = 0,
    quantite_sortie: int = 0,
    current_user = Depends(role_required(["AGENT_STOCK"])),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Get last available quantity
    last_movement = db.query(StockMovement).filter(
        StockMovement.product_id == product_id
    ).order_by(StockMovement.date.desc()).first()
    
    previous_disponible = last_movement.quantite_disponible if last_movement else 0
    new_disponible = previous_disponible + int(quantite_entree) - int(quantite_sortie)
    
    movement = StockMovement(
        product_id=product_id,
        quantite_entree=int(quantite_entree),
        quantite_sortie=int(quantite_sortie),
        quantite_disponible=new_disponible,
        agent_id=current_user.id
    )
    db.add(movement)
    db.commit()
    
    return {
        "message": "Mouvement enregistré",
        "quantite_disponible": new_disponible
    }

@router.get("/current")
def get_current_stock(
    current_user = Depends(role_required(["AGENT_STOCK", "DT", "DG"])),
    db: Session = Depends(get_db)
):
    products = db.query(Product).all()
    result = []
    
    for product in products:
        last_movement = db.query(StockMovement).filter(
            StockMovement.product_id == product.id
        ).order_by(StockMovement.date.desc()).first()
        
        result.append({
            "product_id": product.id,
            "product_nom": product.nom,
            "prix_unitaire": product.prix_unitaire,
            "quantite_disponible": last_movement.quantite_disponible if last_movement else 0,
        })
    
    return result

@router.get("/reports/all")
def get_all_stock_reports(
    current_user = Depends(role_required(["DT", "DG"])),
    db: Session = Depends(get_db)
):
    movements = db.query(StockMovement).order_by(StockMovement.date.desc()).limit(200).all()
    result = []
    for m in movements:
        product = db.query(Product).filter(Product.id == m.product_id).first()
        result.append({
            "date": m.date,
            "product": product.nom if product else "Inconnu",
            "quantite_entree": m.quantite_entree,
            "quantite_sortie": m.quantite_sortie,
            "quantite_disponible": m.quantite_disponible,
        })
    return result
