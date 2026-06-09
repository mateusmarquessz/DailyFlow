def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_update_profile_changes_name_and_theme(client, register_user):
    tokens = register_user(email="profile@example.com")

    response = client.patch(
        "/api/users/me",
        json={"name": "Novo Nome", "theme_preference": "dark"},
        headers=_auth_headers(tokens),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Novo Nome"
    assert body["theme_preference"] == "dark"


def test_change_password_requires_correct_current_password(client, register_user):
    tokens = register_user(email="pwchange@example.com", password="OriginalPass123")

    wrong = client.post(
        "/api/users/me/change-password",
        json={"current_password": "WrongCurrent123", "new_password": "BrandNewPass123"},
        headers=_auth_headers(tokens),
    )
    assert wrong.status_code == 400

    right = client.post(
        "/api/users/me/change-password",
        json={"current_password": "OriginalPass123", "new_password": "BrandNewPass123"},
        headers=_auth_headers(tokens),
    )
    assert right.status_code == 200

    relogin = client.post(
        "/api/auth/login", json={"email": "pwchange@example.com", "password": "BrandNewPass123"}
    )
    assert relogin.status_code == 200


def test_profile_endpoint_requires_authentication(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401
