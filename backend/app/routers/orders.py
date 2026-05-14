"""Router Commandes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Order, OrderItem, Menu, Restaurant
from app.schemas import OrderCreate, OrderOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Commandes"])

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == order_in.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant non trouve")

    total = 0
    order_items = []
    for item in order_in.items:
        menu = db.query(Menu).filter(Menu.id == item.menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail=f"Menu {item.menu_id} non trouve")
        subtotal = menu.price_fcfa * item.quantity
        total += subtotal
        order_items.append(OrderItem(
            menu_id=item.menu_id,
            quantity=item.quantity,
            unit_price_fcfa=menu.price_fcfa,
            notes=item.notes
        ))

    delivery_fee = 500

    order = Order(
        user_id=current_user.id,
        restaurant_id=order_in.restaurant_id,
        delivery_address=order_in.delivery_address,
        delivery_lat=order_in.delivery_lat,
        delivery_lon=order_in.delivery_lon,
        total_amount_fcfa=total,
        delivery_fee_fcfa=delivery_fee,
        payment_method=order_in.payment_method,
    )
    db.add(order)
    db.flush()  # Obtient l ID de la commande

    for item in order_items:
        item.order_id = order.id
        db.add(item)

    db.commit()
    db.refresh(order)
    return order

@router.get("/", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    return order

@router.patch("/{order_id}/status")
def update_status(
    order_id: UUID,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verification manuelle des roles
    if current_user.role not in ["restaurateur", "admin", "livreur"]:
        raise HTTPException(status_code=403, detail="Acces refuse: seuls restaurateur, admin ou livreur peuvent changer le statut")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    
    if current_user.role == "restaurateur":
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id, Restaurant.owner_id == current_user.id).first()
        if not restaurant:
            raise HTTPException(status_code=403, detail="Vous n etes pas le proprietaire de ce restaurant")
    
    if current_user.role == "livreur":
        from app.models import Delivery
        delivery = db.query(Delivery).filter(Delivery.order_id == order_id, Delivery.driver_id == current_user.id).first()
        if not delivery:
            raise HTTPException(status_code=403, detail="Vous n etes pas assigne a cette livraison")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return {"id": str(order.id), "status": order.status}
