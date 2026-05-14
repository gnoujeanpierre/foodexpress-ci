"""ModÃ¨les SQLAlchemy â€” FoodExpress-CI MVP (compatible SQLite)."""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
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
    lat = Column(Float)
    lon = Column(Float)
    opening_hours = Column(JSON)
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
    delivery_lat = Column(Float)
    delivery_lon = Column(Float)
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
    pickup_lat = Column(Float)
    pickup_lon = Column(Float)
    current_lat = Column(Float)
    current_lon = Column(Float)
    status = Column(String(50), default="assigned")
    estimated_delivery_time = Column(DateTime(timezone=True))
    actual_delivery_time = Column(DateTime(timezone=True))
    otp_code = Column(String(6))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
