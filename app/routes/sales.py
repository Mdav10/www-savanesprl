from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import SaleReport, Product, User, ActiviteLog
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/sales", tags=["Sales"])

@router.post("/report")
def create_sale_report(
    product_id: int,
    quantite: int,
    current_user = Depends(role_required(["AGENT_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    montant_total = quantite * product.prix_unitaire
    
    sale = SaleReport(
        product_id=product_id,
        quantite=quantite,
        montant_total=montant_total,
        agent_id=current_user.id
    )
    db.add(sale)
    db.commit()
    
    log = ActiviteLog(
        user_id=current_user.id,
        action="SALE_REPORT",
        details=f"Vente: {quantite}x {product.nom} = {montant_total}€"
    )
    db.add(log)
    db.commit()
    
    return {
        "message": "Rapport de vente enregistré",
        "montant_total": montant_total
    }

@router.get("/my-reports")
def get_my_sales_reports(
    current_user = Depends(role_required(["AGENT_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    reports = db.query(SaleReport).filter(
        SaleReport.agent_id == current_user.id
    ).order_by(SaleReport.date.desc()).all()
    
    result = []
    for r in reports:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        result.append({
            "id": r.id,
            "date": r.date,
            "product": product.nom if product else "Inconnu",
            "quantite": r.quantite,
            "montant_total": r.montant_total
        })
    
    return result

@router.get("/total-revenue")
def get_total_revenue(
    current_user = Depends(role_required(["AGENT_COMMERCIAL", "DIRECTEUR_COMMERCIAL", "DG"])),
    db: Session = Depends(get_db)
):
    total = db.query(func.sum(SaleReport.montant_total)).scalar() or 0
    return {"total_revenue": total}

@router.get("/all-reports")
def get_all_sales_reports(
    current_user = Depends(role_required(["DIRECTEUR_COMMERCIAL", "DG"])),
    db: Session = Depends(get_db)
):
    reports = db.query(SaleReport).order_by(SaleReport.date.desc()).all()
    result = []
    for r in reports:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        agent = db.query(User).filter(User.id == r.agent_id).first()
        result.append({
            "date": r.date,
            "agent": agent.nom if agent else "Inconnu",
            "product": product.nom if product else "Inconnu",
            "quantite": r.quantite,
            "montant_total": r.montant_total
        })
    return result
