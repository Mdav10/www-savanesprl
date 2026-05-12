import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.routes import auth, users, transactions, ventes, logs
from app.routes.auth import create_default_dg

# Create tables
Base.metadata.create_all(bind=engine)

# Create default DG
db = SessionLocal()
try:
    create_default_dg(db)
    db.commit()
except:
    db.rollback()
finally:
    db.close()

app = FastAPI(title="SavaneSPRL API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(ventes.router)
app.include_router(logs.router)

@app.get("/")
def root():
    return {"status": "active", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
