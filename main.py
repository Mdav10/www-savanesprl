import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routes.auth import init_dg

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize DG user
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

# Import routes
from app.routes import auth, users, transactions, products, fix_db_route

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(products.router)
app.include_router(fix_db_route.router)

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
