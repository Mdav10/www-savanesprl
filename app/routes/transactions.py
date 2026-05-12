from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    
    statut = TransactionStatus.APPROUVE if type == "entree" else TransactionStatus.EN_ATTENTE
    
    transaction = Transaction(
        type=type,
        montant=montant,
        libelle=libelle,
        statut=statut,
        cree_par=current_user.id
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": "Transaction créée",
        "transaction_id": transaction.id,
        "statut": statut
    }

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
        message = "Transaction approuvée"
    elif action.upper() == "REJETE":
        transaction.statut = TransactionStatus.REJETE
        message = "Transaction rejetée"
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    transaction.valide_par = current_user.id
    db.commit()
    
    return {"message": message, "transaction_id": transaction_id}

@router.get("/dashboard/dg-daf")
def get_dashboard(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "entree"
    ).scalar() or 0
    
    total_sorties = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.APPROUVE
    ).scalar() or 0
    
    montant_disponible = total_entrees - total_sorties
    pending = db.query(Transaction).filter(Transaction.statut == TransactionStatus.EN_ATTENTE).count()
    
    return {
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "montant_disponible": montant_disponible,
        "validations_en_attente": pending
    }
