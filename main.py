import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routes.auth import create_default_dg

# Create tables
Base.metadata.create_all(bind=engine)

# Create default DG
db = SessionLocal()
create_default_dg(db)
db.close()

app = FastAPI(title="SavaneSPRL")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Dashboard endpoint
@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")

# Import and include routes AFTER app is created
from app.routes import auth, users, products, stock, sales, transactions, reports

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
