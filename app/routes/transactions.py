from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models import Transaction, User, ActiviteLog, TransactionStatus, TransactionType
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.post("/create")
def create_transaction(
    type: str,
    montant: float,
    libelle: str,
    current_user = Depends(role_required(["COMPTABLE"])),
    db: Session = Depends(get_db)
):
    if type not in ["entree", "sortie"]:
        raise HTTPException(status_code=400, detail="Type invalide")
    
    if type == "entree":
        statut = TransactionStatus.APPROUVE
        message = "✅ Entrée enregistrée et approuvée"
    else:
        statut = TransactionStatus.EN_ATTENTE
        message = "⏳ Sortie en attente d'approbation"
    
    transaction = Transaction(
        type=type,
        montant=montant,
        libelle=libelle,
        statut=statut,
        cree_par=current_user.id
    )
    db.add(transaction)
    db.commit()
    
    return {"message": message, "transaction_id": transaction.id, "statut": statut}

@router.post("/validate/{transaction_id}")
def validate_transaction(
    transaction_id: int,
    action: str,
    raison: str = None,
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if transaction.type != "sortie":
        raise HTTPException(status_code=400, detail="Seules les sorties nécessitent validation")
    
    if transaction.statut != TransactionStatus.EN_ATTENTE:
        raise HTTPException(status_code=400, detail=f"Déjà {transaction.statut}")
    
    if action.upper() == "APPROUVE":
        transaction.statut = TransactionStatus.APPROUVE
        message = f"✅ Approuvée par {current_user.role_id}"
    elif action.upper() == "REJETE":
        transaction.statut = TransactionStatus.REJETE
        if not raison:
            raise HTTPException(status_code=400, detail="Une raison est requise pour le rejet")
        transaction.raison_rejet = raison
        message = f"❌ Rejetée par {current_user.role_id}: {raison}"
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    transaction.valide_par = current_user.id
    db.commit()
    
    return {"message": message, "transaction_id": transaction_id}

@router.get("/pending")
def get_pending_transactions(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    pending = db.query(Transaction).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.EN_ATTENTE
    ).order_by(Transaction.date.desc()).all()
    
    return [
        {
            "id": t.id,
            "montant": t.montant,
            "libelle": t.libelle,
            "date": t.date,
            "cree_par": t.cree_par
        }
        for t in pending
    ]

@router.get("/dashboard")
def get_financial_dashboard(
    current_user = Depends(role_required(["DG", "DAF", "COMPTABLE"])),
    db: Session = Depends(get_db)
):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "entree"
    ).scalar() or 0
    
    total_sorties = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.APPROUVE
    ).scalar() or 0
    
    solde = total_entrees - total_sorties
    
    transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(100).all()
    
    return {
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "solde": solde,
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "montant": t.montant,
                "libelle": t.libelle,
                "statut": t.statut,
                "raison_rejet": t.raison_rejet,
                "date": t.date
            }
            for t in transactions
        ]
    }

@router.get("/reports/date-range")
def get_transactions_by_date(
    start_date: str,
    end_date: str,
    current_user = Depends(role_required(["COMPTABLE", "DG", "DAF"])),
    db: Session = Depends(get_db)
):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    transactions = db.query(Transaction).filter(
        Transaction.date >= start,
        Transaction.date <= end
    ).order_by(Transaction.date.desc()).all()
    
    return [
        {
            "date": t.date,
            "type": t.type,
            "montant": t.montant,
            "libelle": t.libelle,
            "statut": t.statut
        }
        for t in transactions
    ]
