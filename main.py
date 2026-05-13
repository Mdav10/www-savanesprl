import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routes import auth, users, products, stock, sales, transactions, reports
from app.routes.auth import create_default_dg

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    create_default_dg(db)
    db.commit()
except:
    db.rollback()
finally:
    db.close()

app = FastAPI(title="SavaneSPRL API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(stock.router)
app.include_router(sales.router)
app.include_router(transactions.router)
app.include_router(reports.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
