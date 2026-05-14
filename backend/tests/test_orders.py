"""Tests Commandes."""
def test_create_order(client, auth_headers, test_restaurant, test_menu):
    response = client.post("/orders/", headers=auth_headers, json={
        "restaurant_id": str(test_restaurant.id),
        "delivery_address": "Abidjan, Angré",
        "delivery_lat": 5.35,
        "delivery_lon": -4.00,
        "items": [
            {"menu_id": str(test_menu.id), "quantity": 2, "notes": "Sans piment"}
        ],
        "payment_method": "orange_money"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["total_amount_fcfa"] == 7000  # 3500 * 2

def test_list_orders(client, auth_headers, test_restaurant, test_menu):
    # Cree une commande d abord
    client.post("/orders/", headers=auth_headers, json={
        "restaurant_id": str(test_restaurant.id),
        "delivery_address": "Abidjan, Angré",
        "delivery_lat": 5.35,
        "delivery_lon": -4.00,
        "items": [{"menu_id": str(test_menu.id), "quantity": 1}],
        "payment_method": "cash"
    })
    response = client.get("/orders/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_update_status_by_resto(client, resto_headers, test_restaurant, test_menu, db_session):
    from app.models import User, Order
    # Cree un client et une commande
    user = User(
        email="client2@example.com",
        phone="04050607",
        password_hash="fakehash",
        full_name="Client 2",
        role="client"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    order = Order(
        user_id=user.id,
        restaurant_id=test_restaurant.id,
        delivery_address="Test",
        delivery_lat=5.0,
        delivery_lon=-4.0,
        total_amount_fcfa=3500,
        delivery_fee_fcfa=500,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    response = client.patch(f"/orders/{order.id}/status?new_status=preparing", headers=resto_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "preparing"

def test_update_status_forbidden_for_client(client, auth_headers, test_restaurant, test_menu, db_session):
    from app.models import Order
    # Cree une commande pour le client auth_headers
    # Le client auth_headers correspond a test_user (phone 01020304)
    from app.models import User
    user = db_session.query(User).filter(User.phone == "01020304").first()
    order = Order(
        user_id=user.id,
        restaurant_id=test_restaurant.id,
        delivery_address="Test",
        delivery_lat=5.0,
        delivery_lon=-4.0,
        total_amount_fcfa=3500,
        delivery_fee_fcfa=500,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    response = client.patch(f"/orders/{order.id}/status?new_status=preparing", headers=auth_headers)
    assert response.status_code == 403  # Client ne peut pas changer le statut
