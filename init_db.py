from app.database import engine, Base
from app.models import User, Product, StockMovement, SaleReport, Transaction, ActiviteLog
from app.utils import get_password_hash
from sqlalchemy import inspect

print("Creating all tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Tables created!")

from app.database import SessionLocal
db = SessionLocal()

# Create DG user
dg = db.query(User).filter(User.username == "OsiasHab").first()
if not dg:
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
    print("✅ DG created: OsiasHab")
else:
    print("✅ DG already exists")

# Create sample products
if db.query(Product).count() == 0:
    products = [
        Product(nom="Produit A", prix_unitaire=100),
        Product(nom="Produit B", prix_unitaire=250),
        Product(nom="Produit C", prix_unitaire=500),
    ]
    for p in products:
        db.add(p)
    db.commit()
    print("✅ Sample products created")

db.close()
print("Database initialization complete!")
