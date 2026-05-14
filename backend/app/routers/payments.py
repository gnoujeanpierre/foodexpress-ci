"""Router Paiement — structure pour Orange Money / MTN MoMo."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import User, Order
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/payments", tags=["Paiement"])

@router.post("/{order_id}/initiate")
def initiate_payment(
    order_id: UUID,
    method: str,  # "orange_money", "mtn_momo", "cash"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Commande deja payee")

    # Simulation du processus de paiement
    # En production: appel API Orange Money / MTN MoMo ici
    reference = f"PAY-{order_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    order.payment_method = method
    order.payment_reference = reference
    order.payment_status = "pending"
    db.commit()
    db.refresh(order)

    return {
        "order_id": str(order.id),
        "amount_fcfa": order.total_amount_fcfa + order.delivery_fee_fcfa,
        "method": method,
        "reference": reference,
        "status": "pending",
        "message": f"Paiement de {order.total_amount_fcfa + order.delivery_fee_fcfa} FCFA initie via {method}. Reference: {reference}",
        "instructions": "Validez le paiement sur votre telephone (simulation)"
    }

@router.post("/{order_id}/confirm")
def confirm_payment(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "restaurateur"))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    if order.payment_status != "pending":
        raise HTTPException(status_code=400, detail="Aucun paiement en attente")

    # Simulation confirmation
    order.payment_status = "paid"
    order.status = "paid"  # Passe a preparing ensuite
    db.commit()
    db.refresh(order)

    return {
        "order_id": str(order.id),
        "status": "paid",
        "reference": order.payment_reference,
        "message": "Paiement confirme avec succes"
    }

@router.post("/{order_id}/simulate-callback")
def simulate_callback(
    order_id: UUID,
    status: str = "success",
    db: Session = Depends(get_db)
):
    """Endpoint de test pour simuler le callback du operateur mobile."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")

    if status == "success":
        order.payment_status = "paid"
        order.status = "paid"
    else:
        order.payment_status = "failed"

    db.commit()
    db.refresh(order)

    return {
        "order_id": str(order.id),
        "payment_status": order.payment_status,
        "order_status": order.status
    }

@router.get("/{order_id}/status")
def payment_status(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    if str(order.user_id) != str(current_user.id) and current_user.role not in ["admin", "restaurateur"]:
        raise HTTPException(status_code=403, detail="Acces refuse")

    return {
        "order_id": str(order.id),
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        "amount_fcfa": order.total_amount_fcfa + order.delivery_fee_fcfa
    }
