from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/transactions")

@router.get("/dashboard")
def get_dashboard(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "total_entrees": 0,
        "total_sorties": 0,
        "solde": 0,
        "message": "Module financier en cours de développement"
    }
