from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ActiviteLog
from app.auth import role_required

router = APIRouter(prefix="/api/logs", tags=["Logs"])

@router.get("/")
def get_logs(
    current_user = Depends(role_required(["DG"])),
    db: Session = Depends(get_db)
):
    logs = db.query(ActiviteLog).order_by(ActiviteLog.date.desc()).limit(100).all()
    return [
        {"user_id": l.user_id, "action": l.action, "details": l.details, "date": l.date}
        for l in logs
    ]
