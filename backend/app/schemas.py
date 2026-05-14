"""Schemas Pydantic — validation & serialisation."""
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
