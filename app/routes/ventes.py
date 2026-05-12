from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Vente, User, ActiviteLog, Stock
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/ventes", tags=["Ventes"])

@router.post("/create")
def create_vente(
    produit: str,
    quantite: int,
    prix_unitaire: float,
    current_user = Depends(role_required(["AGENT_MARKETING"])),
    db: Session = Depends(get_db)
):
    montant_total = quantite * prix_unitaire
    
    vente = Vente(
        produit=produit,
        quantite=quantite,
        prix_unitaire=prix_unitaire,
        montant_total=montant_total,
        agent_id=current_user.id
    )
    db.add(vente)
    
    stock = db.query(Stock).filter(Stock.produit == produit).first()
    if stock:
        stock.quantite_sortie += quantite
        stock.quantite_disponible -= quantite
    else:
        new_stock = Stock(
            produit=produit,
            quantite_sortie=quantite,
            quantite_disponible=-quantite
        )
        db.add(new_stock)
    
    db.commit()
    
    return {"message": "Vente enregistrée", "montant_total": montant_total}

@router.get("/commercial/dashboard")
def commercial_dashboard(
    current_user = Depends(role_required(["DIRECTEUR_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    total_quantite = db.query(func.sum(Vente.quantite)).scalar() or 0
    
    perfs = db.query(
        Vente.agent_id,
        User.nom,
        func.sum(Vente.quantite).label('total_quantite'),
        func.sum(Vente.montant_total).label('total_montant')
    ).join(User, Vente.agent_id == User.id).group_by(Vente.agent_id, User.nom).all()
    
    stock = db.query(Stock).all()
    
    return {
        "quantite_vendue_totale": total_quantite,
        "performance_agents": [
            {"agent": p.nom, "quantite": p.total_quantite, "montant": p.total_montant}
            for p in perfs
        ],
        "stock": [{"produit": s.produit, "disponible": s.quantite_disponible} for s in stock]
    }

@router.get("/agent/my-ventes")
def get_my_ventes(
    current_user = Depends(role_required(["AGENT_MARKETING"])),
    db: Session = Depends(get_db)
):
    ventes = db.query(Vente).filter(Vente.agent_id == current_user.id).all()
    return [
        {"produit": v.produit, "quantite": v.quantite, "prix_unitaire": v.prix_unitaire, "date": v.date}
        for v in ventes
    ]
