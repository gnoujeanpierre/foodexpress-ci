import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine
from app.models import Base, Restaurant, Menu, User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
Base.metadata.create_all(bind=engine)
db = SessionLocal()

db.query(Menu).delete()
db.query(Restaurant).delete()
db.query(User).delete()
db.commit()

admin = User(email='admin@foodexpress.ci', phone='+22501010101', password_hash=pwd_context.hash('admin12'), full_name='Admin', role=UserRole.ADMIN)
db.add(admin)
db.commit()

r1 = Restaurant(name='Maquis Chez Kofi', description='Maquis ivoirien', address='Cocody', lat=5.358, lon=-4.001, opening_hours={'lundi':'11h-22h'}, commission_rate=0.15, is_open=True)
r2 = Restaurant(name='Burger Zone', description='Fast food', address='Plateau', lat=5.336, lon=-4.026, opening_hours={'lundi':'10h-23h'}, commission_rate=0.18, is_open=True)
r3 = Restaurant(name='Patisserie Douceur', description='Patisserie', address='Treichville', lat=5.303, lon=-4.015, opening_hours={'lundi':'07h-20h'}, commission_rate=0.12, is_open=True)
db.add_all([r1, r2, r3])
db.commit()

for r in [r1, r2, r3]:
    db.refresh(r)

menus = [
    Menu(restaurant_id=r1.id, name='Attieke Poisson', description='Attieke avec poisson', price_fcfa=3500, category='Plats', preparation_time_min=20, is_available=True),
    Menu(restaurant_id=r1.id, name='Alloco Oeuf', description='Alloco avec oeuf', price_fcfa=1500, category='Snack', preparation_time_min=10, is_available=True),
    Menu(restaurant_id=r1.id, name='Garba', description='Attieke thon', price_fcfa=1000, category='Snack', preparation_time_min=5, is_available=True),
    Menu(restaurant_id=r1.id, name='Poulet Braise', description='Poulet avec alloco', price_fcfa=5000, category='Plats', preparation_time_min=25, is_available=True),
    Menu(restaurant_id=r2.id, name='Classic Burger', description='Burger boeuf', price_fcfa=3000, category='Burgers', preparation_time_min=12, is_available=True),
    Menu(restaurant_id=r2.id, name='Double Cheese', description='Double steak', price_fcfa=4500, category='Burgers', preparation_time_min=15, is_available=True),
    Menu(restaurant_id=r2.id, name='Frites XL', description='Frites', price_fcfa=1500, category='Accompagnements', preparation_time_min=8, is_available=True),
    Menu(restaurant_id=r2.id, name='Milkshake', description='Milkshake vanille', price_fcfa=2000, category='Boissons', preparation_time_min=5, is_available=True),
    Menu(restaurant_id=r3.id, name='Croissant', description='Croissant beurre', price_fcfa=800, category='Viennoiseries', preparation_time_min=3, is_available=True),
    Menu(restaurant_id=r3.id, name='Gateau Chocolat', description='Gateau', price_fcfa=2500, category='Patisseries', preparation_time_min=5, is_available=True),
]

for m in menus:
    db.add(m)
db.commit()
db.close()

print('OK - Donnees inserees')
print('Restaurants: 3, Menus: 10')
print('Admin: admin@foodexpress.ci / admin12')
