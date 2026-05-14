"""Point d entree FastAPI â€” FoodExpress-CI MVP."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, restaurants, orders, deliveries

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FoodExpress-CI API",
    description="API backend pour l application de livraison de repas a Abidjan",
    version="1.1.0",
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
app.include_router(orders.router)
app.include_router(deliveries.router)

@app.get("/")
def root():
    return {"message": "FoodExpress-CI API â€” La TEC", "status": "operational", "version": "1.1.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
