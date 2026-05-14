import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routes.auth import init_dg

Base.metadata.create_all(bind=engine)

db = SessionLocal()
init_dg(db)
db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import auth, users, transactions
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "SavaneSPRL API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
