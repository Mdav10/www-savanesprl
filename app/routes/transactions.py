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
    
    # ENTRÉE = direct approval, SORTIE = needs approval
    if type == "entree":
        statut = TransactionStatus.APPROUVE
        message = "✅ Entrée enregistrée et approuvée"
    else:
        statut = TransactionStatus.EN_ATTENTE
        message = "⏳ Sortie enregistrée en attente d'approbation DG/DAF"
    
    transaction = Transaction(
        type=type,
        montant=montant,
        libelle=libelle,
        statut=statut,
        cree_par=current_user.id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    log = ActiviteLog(
        user_id=current_user.id,
        action="CREATE_TRANSACTION",
        details=f"Créé {type} de {montant}€: {libelle} - Statut: {statut}"
    )
    db.add(log)
    db.commit()
    
    return {
        "message": message,
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
        raise HTTPException(status_code=400, detail=f"Déjà {transaction.statut}")
    
    if action.upper() == "APPROUVE":
        transaction.statut = TransactionStatus.APPROUVE
        message = f"✅ Sortie #{transaction_id} approuvée par {current_user.role_id}"
    elif action.upper() == "REJETE":
        transaction.statut = TransactionStatus.REJETE
        message = f"❌ Sortie #{transaction_id} rejetée par {current_user.role_id}"
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    
    transaction.valide_par = current_user.id
    db.commit()
    
    log = ActiviteLog(
        user_id=current_user.id,
        action="VALIDATE_TRANSACTION",
        details=message
    )
    db.add(log)
    db.commit()
    
    return {"message": message, "transaction_id": transaction_id, "new_status": transaction.statut}

@router.get("/pending")
def get_pending_validations(
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

@router.get("/dashboard/dg-daf")
def get_dg_daf_dashboard(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "entree"
    ).scalar() or 0
    
    total_sorties_validees = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.APPROUVE
    ).scalar() or 0
    
    total_sorties_attente = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.EN_ATTENTE
    ).scalar() or 0
    
    montant_disponible = total_entrees - total_sorties_validees
    pending_count = db.query(Transaction).filter(
        Transaction.type == "sortie",
        Transaction.statut == TransactionStatus.EN_ATTENTE
    ).count()
    
    # All transactions for reports
    all_transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(100).all()
    
    return {
        "total_entrees": total_entrees,
        "total_sorties_validees": total_sorties_validees,
        "total_sorties_attente": total_sorties_attente,
        "montant_disponible": montant_disponible,
        "validations_en_attente": pending_count,
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "montant": t.montant,
                "libelle": t.libelle,
                "statut": t.statut,
                "date": t.date
            }
            for t in all_transactions
        ]
    }

@router.get("/journal")
def get_journal(
    current_user = Depends(role_required(["COMPTABLE", "DG", "DAF"])),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(100).all()
    return [
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
