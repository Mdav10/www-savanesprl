from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database import get_db, engine
from app.auth import get_current_user

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/check-db")
def check_db(current_user = Depends(get_current_user), db = Depends(get_db)):
    if current_user.role != "DG":
        return {"error": "Unauthorized"}
    
    # Check table structure
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = [{"column": row[0], "type": row[1]} for row in result]
    
    # Count users
    user_count = db.query(User).count()
    
    return {
        "columns": columns,
        "user_count": user_count,
        "dg_user_exists": db.query(User).filter(User.username == "OsiasHab").first() is not None
    }
