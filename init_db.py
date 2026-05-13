from app.database import engine, SessionLocal
from app.models import Base, User, Transaction, Product, StockMovement, SaleReport
from app.utils import get_password_hash

# Drop and recreate all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create DG user only
dg = User(
    nom="Directeur General",
    email="dg@savanesprl.com",
    username="OsiasHab",
    mot_de_passe=get_password_hash("08800Osi"),
    role_id="DG",
    is_active=True
)
db.add(dg)
db.commit()

print("✅ Database reset complete!")
print("✅ DG created: OsiasHab / 08800Osi")
print("✅ No fake transactions - everything at 0")

db.close()
