from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Transaction
from app.auth import get_current_user

router = APIRouter(prefix="/api/transactions")

@router.get("/dashboard")
def get_dashboard(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(Transaction.type == "entree").scalar() or 0
    total_sorties = db.query(func.sum(Transaction.montant)).filter(Transaction.type == "sortie").scalar() or 0
    
    return {
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "solde": total_entrees - total_sorties
    }
