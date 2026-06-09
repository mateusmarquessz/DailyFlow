def test_register_creates_user_and_returns_tokens(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Mateus", "email": "mateus@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "mateus@example.com"
    assert body["user"]["name"] == "Mateus"
    assert "hashed_password" not in body["user"]
    assert body["access_token"]
    assert body["refresh_token"]


def test_register_rejects_duplicate_email(client, register_user):
    register_user(email="dup@example.com")

    response = client.post(
        "/api/auth/register",
        json={"name": "Outro", "email": "dup@example.com", "password": "AnotherPass123"},
    )

    assert response.status_code == 409


def test_login_with_correct_credentials_returns_tokens(client, register_user):
    register_user(email="login@example.com", password="CorrectPass123")

    response = client.post(
        "/api/auth/login", json={"email": "login@example.com", "password": "CorrectPass123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "login@example.com"
    assert body["access_token"]


def test_login_with_wrong_password_is_rejected(client, register_user):
    register_user(email="wrongpass@example.com", password="CorrectPass123")

    response = client.post(
        "/api/auth/login", json={"email": "wrongpass@example.com", "password": "WrongPass123"}
    )

    assert response.status_code == 401


def test_me_requires_bearer_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, register_user):
    tokens = register_user(email="me@example.com")

    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_refresh_token_issues_new_access_token(client, register_user):
    tokens = register_user(email="refresh@example.com")

    response = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_refresh_with_revoked_token_after_logout_is_rejected(client, register_user):
    tokens = register_user(email="logout@example.com")

    logout_response = client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_response.status_code == 200

    refresh_response = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 401


def test_forgot_password_does_not_leak_account_existence(client, register_user):
    register_user(email="forgot@example.com")

    known = client.post("/api/auth/forgot-password", json={"email": "forgot@example.com"})
    unknown = client.post("/api/auth/forgot-password", json={"email": "ghost@example.com"})

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json()["message"] == unknown.json()["message"]


def test_reset_password_with_invalid_token_fails(client):
    response = client.post(
        "/api/auth/reset-password", json={"token": "not-a-real-token", "new_password": "NewStrongPass123"}
    )
    assert response.status_code == 400
