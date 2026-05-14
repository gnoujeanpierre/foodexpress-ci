"""Configuration pytest — DB en memoire, client HTTP, fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, UserRole, Restaurant, Menu, OrderStatus
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DB SQLite en memoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        phone="01020304",
        password_hash=pwd_context.hash("password123"),
        full_name="Test User",
        role=UserRole.CLIENT,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_restaurateur(db_session):
    user = User(
        email="resto@example.com",
        phone="02030405",
        password_hash=pwd_context.hash("password123"),
        full_name="Restaurateur Test",
        role=UserRole.RESTAURATEUR,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_restaurant(db_session, test_restaurateur):
    restaurant = Restaurant(
        owner_id=test_restaurateur.id,
        name="Chez Abidjan",
        description="Restaurant ivoirien",
        address="Abidjan, Cocody",
        lat=5.36,
        lon=-4.01,
        is_open=True,
    )
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)
    return restaurant

@pytest.fixture
def test_menu(db_session, test_restaurant):
    menu = Menu(
        restaurant_id=test_restaurant.id,
        name="Attieke Poisson",
        description="Attieke avec poisson braise",
        price_fcfa=3500,
        is_available=True,
    )
    db_session.add(menu)
    db_session.commit()
    db_session.refresh(menu)
    return menu

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/login", data={
        "username": test_user.phone,
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def resto_headers(client, test_restaurateur):
    response = client.post("/auth/login", data={
        "username": test_restaurateur.phone,
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
