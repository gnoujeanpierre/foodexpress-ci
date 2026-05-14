"""Tests Authentification."""
def test_register(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "phone": "03040506",
        "password": "password123",
        "full_name": "Nouvel Utilisateur",
        "role": "client"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_phone(client, test_user):
    response = client.post("/auth/register", json={
        "email": "other@example.com",
        "phone": test_user.phone,
        "password": "password123",
        "full_name": "Duplicate",
        "role": "client"
    })
    assert response.status_code == 400
    assert "Telephone deja utilise" in response.json()["detail"]

def test_login(client, test_user):
    response = client.post("/auth/login", data={
        "username": test_user.phone,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(client, test_user):
    response = client.post("/auth/login", data={
        "username": test_user.phone,
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_read_me(client, auth_headers, test_user):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["phone"] == test_user.phone
    assert data["role"] == "client"
