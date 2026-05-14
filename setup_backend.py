import os

base = "backend"
os.makedirs(f"{base}/app/routers", exist_ok=True)

files = {
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.14.0
pydantic[email]==2.9.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.17
redis==5.2.0
httpx==0.27.2
python-dotenv==1.0.1
""",
    "app/__init__.py": "",
    "app/routers/__init__.py": "",
    "app/database.py": '''\"\"\"Configuration base de donnees PostgreSQL + PostGIS.\"\"\"
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://foodexpress:foodexpress_dev@localhost:5432/foodexpress_ci")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
    "app/models.py": '''\"\"\"Modeles SQLAlchemy — FoodExpress-CI MVP.\"\"\"
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    CLIENT = "client"
    RESTAURATEUR = "restaurateur"
    LIVREUR = "livreur"
    ADMIN = "admin"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text)
    location = Column(Geometry("POINT", srid=4326))
    opening_hours = Column(JSONB)
    is_open = Column(Boolean, default=True)
    commission_rate = Column(Float, default=0.15)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Menu(Base):
    __tablename__ = "menus"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price_fcfa = Column(Integer, nullable=False)
    image_url = Column(String(500))
    category = Column(String(100))
    is_available = Column(Boolean, default=True)
    preparation_time_min = Column(Integer, default=15)

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"))
    delivery_address = Column(Text)
    delivery_location = Column(Geometry("POINT", srid=4326))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount_fcfa = Column(Integer, default=0)
    delivery_fee_fcfa = Column(Integer, default=0)
    payment_method = Column(String(20))
    payment_status = Column(String(20), default="pending")
    payment_reference = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    menu_id = Column(UUID(as_uuid=True), ForeignKey("menus.id"))
    quantity = Column(Integer, default=1)
    unit_price_fcfa = Column(Integer)
    notes = Column(Text)

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    pickup_location = Column(Geometry("POINT", srid=4326))
    current_location = Column(Geometry("POINT", srid=4326))
    status = Column(String(50), default="assigned")
    estimated_delivery_time = Column(DateTime(timezone=True))
    actual_delivery_time = Column(DateTime(timezone=True))
    otp_code = Column(String(6))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
''',
    "app/schemas.py": '''\"\"\"Schemas Pydantic — validation & serialisation.\"\"\"
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    phone: str
    password: str
    full_name: str
    role: str = "client"

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RestaurantOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    address: Optional[str]
    is_open: bool
    commission_rate: float
    class Config:
        from_attributes = True

class MenuOut(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str]
    price_fcfa: int
    image_url: Optional[str]
    category: Optional[str]
    is_available: bool
    preparation_time_min: int
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    menu_id: UUID
    quantity: int = 1
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    restaurant_id: UUID
    delivery_address: str
    delivery_lat: float
    delivery_lon: float
    items: List[OrderItemCreate]
    payment_method: str

class OrderOut(BaseModel):
    id: UUID
    status: str
    total_amount_fcfa: int
    delivery_fee_fcfa: int
    payment_status: str
    created_at: datetime
    class Config:
        from_attributes = True
''',
    "app/routers/auth.py": '''\"\"\"Router Authentification JWT.\"\"\"
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, Token

router = APIRouter(prefix="/auth", tags=["Authentification"])

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == user_in.phone).first():
        raise HTTPException(status_code=400, detail="Telephone deja utilise")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email deja utilise")
    user = User(
        email=user_in.email,
        phone=user_in.phone,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Telephone ou mot de passe incorrect")
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    return {"id": str(user.id), "email": user.email, "phone": user.phone, "role": user.role, "full_name": user.full_name}
''',
    "app/main.py": '''\"\"\"Point d entree FastAPI — FoodExpress-CI MVP.\"\"\"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth

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

@app.get("/")
ndef root():
    return {"message": "FoodExpress-CI API — La TEC", "status": "operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
'''
}

for path, content in files.items():
    with open(f"{base}/{path}", "w", encoding="utf-8") as f:
        f.write(content)

print("OK - 10 fichiers crees")
