from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Transaction, TransactionStatus, TransactionType
from app.deps import get_current_user, role_required

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
    
    if montant <= 0:
        raise HTTPException(status_code=400, detail="Le montant doit être positif")
    
    if type == "entree":
        statut = TransactionStatus.APPROUVE
        message = "✅ Entrée enregistrée"
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
    
    return {"message": message, "transaction_id": transaction.id}

@router.post("/validate/{transaction_id}")
def validate_transaction(
    transaction_id: int,
    action: str,
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if transaction.type != "sortie":
        raise HTTPException(status_code=400, detail="Seules les sorties nécessitent validation")
    
    if transaction.statut != TransactionStatus.EN_ATTENTE:
        raise HTTPException(status_code=400, detail="Déjà traitée")
    
    if action.upper() == "APPROUVE":
        transaction.statut = TransactionStatus.APPROUVE
    elif action.upper() == "REJETE":
        transaction.statut = TransactionStatus.REJETE
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    transaction.valide_par = current_user.id
    db.commit()
    
    return {"message": f"Transaction {action.lower()}e"}

@router.get("/pending")
def get_pending(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    pending = db.query(Transaction).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.EN_ATTENTE
    ).order_by(Transaction.date.desc()).all()
    
    return [
        {"id": t.id, "montant": t.montant, "libelle": t.libelle, "date": t.date}
        for t in pending
    ]

@router.get("/dashboard")
def get_dashboard(
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
                "date": t.date
            }
            for t in transactions
        ]
    }

@router.post("/reset")
def reset_transactions(
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    deleted = db.query(Transaction).delete()
    db.commit()
    return {"message": f"✅ {deleted} transactions supprimées", "deleted_count": deleted}
