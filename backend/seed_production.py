"""Script insertion donnees — Production PostgreSQL (Render)."""
import sys
import os
sys.path.insert(0, ".")

from app.database import SessionLocal, engine
from app.models import Base, Restaurant, Menu, User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Creer les tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Verifier si donnees existent deja
existing = db.query(Restaurant).first()
if existing:
    print("Donnees deja presentes. Skip.")
    db.close()
    sys.exit(0)

print("Insertion donnees de test...")

admin = User(email="admin@foodexpress.ci", phone="+22501010101", password_hash=pwd_context.hash("admin12"), full_name="Admin RestoGroup", role=UserRole.ADMIN)
db.add(admin)
db.commit()

r1 = Restaurant(name="Maquis Chez Kofi", description="Authentique maquis ivoirien", address="Rue des Jardins, Cocody, Abidjan", lat=5.358, lon=-4.001, opening_hours={"lundi": "11h-22h", "mardi": "11h-22h", "mercredi": "11h-22h", "jeudi": "11h-22h", "vendredi": "11h-23h", "samedi": "11h-23h", "dimanche": "12h-21h"}, commission_rate=0.15, is_open=True)
r2 = Restaurant(name="Burger Zone Abidjan", description="Fast-food gourmet", address="Boulevard de la Republique, Plateau, Abidjan", lat=5.336, lon=-4.026, opening_hours={"lundi": "10h-23h", "mardi": "10h-23h", "mercredi": "10h-23h", "jeudi": "10h-23h", "vendredi": "10h-00h", "samedi": "10h-00h", "dimanche": "11h-22h"}, commission_rate=0.18, is_open=True)
r3 = Restaurant(name="Patisserie Douceur", description="Patisserie fine", address="Rue 12, Treichville, Abidjan", lat=5.303, lon=-4.015, opening_hours={"lundi": "07h-20h", "mardi": "07h-20h", "mercredi": "07h-20h", "jeudi": "07h-20h", "vendredi": "07h-21h", "samedi": "07h-21h", "dimanche": "08h-18h"}, commission_rate=0.12, is_open=True)

db.add_all([r1, r2, r3])
db.commit()

for r in [r1, r2, r3]:
    db.refresh(r)

menus = [
    Menu(restaurant_id=r1.id, name="Attieke Poisson", description="Attieke frais avec poisson braise", price_fcfa=3500, category="Plats", preparation_time_min=20, is_available=True),
    Menu(restaurant_id=r1.id, name="Alloco Oeuf", description="Banane plantain frite avec oeuf", price_fcfa=1500, category="Snack", preparation_time_min=10, is_available=True),
    Menu(restaurant_id=r1.id, name="Garba", description="Attieke avec thon en sauce", price_fcfa=1000, category="Snack", preparation_time_min=5, is_available=True),
    Menu(restaurant_id=r1.id, name="Poulet Braise", description="Demi-poulet braise avec alloco", price_fcfa=5000, category="Plats", preparation_time_min=25, is_available=True),
    Menu(restaurant_id=r2.id, name="Classic Burger", description="Boeuf 150g, cheddar, salade", price_fcfa=3000, category="Burgers", preparation_time_min=12, is_available=True),
    Menu(restaurant_id=r2.id, name="Double Cheese", description="Double steak, double cheddar", price_fcfa=4500, category="Burgers", preparation_time_min=15, is_available=True),
    Menu(restaurant_id=r2.id, name="Frites XL", description="Grand format frites fraiches", price_fcfa=1500, category="Accompagnements", preparation_time_min=8, is_available=True),
    Menu(restaurant_id=r2.id, name="Milkshake Vanille", description="Milkshake onctueux vanille", price_fcfa=2000, category="Boissons", preparation_time_min=5, is_available=True),
    Menu(restaurant_id=r3.id, name="Croissant Beurre", description="Croissant pur beurre croustillant", price_fcfa=800, category="Viennoiseries", preparation_time_min=3, is_available=True),
    Menu(restaurant_id=r3.id, name="Gateau Chocolat", description="Part individuelle chocolat", price_fcfa=2500, category="Patisseries", preparation_time_min=5, is_available=True),
]

for m in menus:
    db.add(m)

db.commit()
db.close()

print("OK - Donnees inserees en production")
print("Restaurants: 3, Menus: 10, Admin: admin@foodexpress.ci / admin12")
