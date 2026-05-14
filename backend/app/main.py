"""Point d entree FastAPI — FoodExpress-CI MVP."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, restaurants

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FoodExpress-CI API",
    description="API backend pour l application de livraison de repas a Abidjan",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(restaurants.router)

@app.get("/")
def root():
    return {"message": "FoodExpress-CI API — La TEC", "status": "operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
