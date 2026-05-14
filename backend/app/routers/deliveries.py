"""Router Livraisons."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Order, Delivery
from app.routers.auth import get_current_user

router = APIRouter(prefix="/deliveries", tags=["Livraisons"])

@router.post("/{order_id}", status_code=status.HTTP_201_CREATED)
def create_delivery(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    if db.query(Delivery).filter(Delivery.order_id == order_id).first():
        raise HTTPException(status_code=400, detail="Livraison deja creee")

    delivery = Delivery(order_id=order_id)
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return {
        "id": str(delivery.id),
        "order_id": str(delivery.order_id),
        "status": delivery.status,
        "created_at": delivery.created_at
    }

@router.get("/")
def list_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deliveries = db.query(Delivery).all()
    result = []
    for d in deliveries:
        result.append({
            "id": str(d.id),
            "order_id": str(d.order_id),
            "driver_id": str(d.driver_id) if d.driver_id else None,
            "status": d.status,
            "current_lat": d.current_lat,
            "current_lon": d.current_lon,
            "created_at": d.created_at
        })
    return result

@router.get("/{delivery_id}")
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Livraison non trouvee")
    return {
        "id": str(d.id),
        "order_id": str(d.order_id),
        "driver_id": str(d.driver_id) if d.driver_id else None,
        "status": d.status,
        "current_lat": d.current_lat,
        "current_lon": d.current_lon,
        "pickup_lat": d.pickup_lat,
        "pickup_lon": d.pickup_lon,
        "estimated_delivery_time": d.estimated_delivery_time,
        "actual_delivery_time": d.actual_delivery_time,
        "otp_code": d.otp_code,
        "created_at": d.created_at
    }

@router.patch("/{delivery_id}/assign")
def assign_driver(
    delivery_id: UUID,
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Livraison non trouvee")
    delivery.driver_id = driver_id
    db.commit()
    db.refresh(delivery)
    return {"id": str(delivery.id), "driver_id": str(delivery.driver_id), "status": delivery.status}

@router.patch("/{delivery_id}/track")
def track_delivery(
    delivery_id: UUID,
    lat: float,
    lon: float,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Livraison non trouvee")
    delivery.current_lat = lat
    delivery.current_lon = lon
    if status:
        delivery.status = status
    db.commit()
    db.refresh(delivery)
    return {
        "id": str(delivery.id),
        "current_lat": delivery.current_lat,
        "current_lon": delivery.current_lon,
        "status": delivery.status
    }
