"""Router Commandes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Order, OrderItem, Menu, OrderStatus
from app.schemas import OrderCreate, OrderOut, OrderItemCreate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Commandes"])

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verifier le restaurant existe
    from app.models import Restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.id == order_in.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant non trouve")

    # Calculer le total
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

    # Frais de livraison fixes (a adapter)
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
        items=order_items
    )
    db.add(order)
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
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    # TODO: verifier les permissions selon le role
    order.status = new_status
    db.commit()
    db.refresh(order)
    return {"id": str(order.id), "status": order.status}
