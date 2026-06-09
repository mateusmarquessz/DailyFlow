def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_goal(client, headers, **overrides):
    payload = {
        "title": "Ler 4 livros",
        "description": "Meta de leitura do trimestre",
        "type": "monthly",
        "target_value": 4,
        "deadline": "2026-12-31",
    }
    payload.update(overrides)
    response = client.post("/api/goals", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_list_goals(client, register_user):
    tokens = register_user(email="goals1@example.com")
    headers = _auth_headers(tokens)

    created = _create_goal(client, headers)
    assert created["status"] == "in_progress"
    assert created["current_value"] == 0
    assert created["progress_percent"] == 0

    response = client.get("/api/goals", headers=headers)
    assert response.status_code == 200
    titles = [goal["title"] for goal in response.json()]
    assert "Ler 4 livros" in titles


def test_get_update_and_delete_goal(client, register_user):
    tokens = register_user(email="goals2@example.com")
    headers = _auth_headers(tokens)
    goal = _create_goal(client, headers)

    get_response = client.get(f"/api/goals/{goal['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == goal["id"]

    update_response = client.patch(
        f"/api/goals/{goal['id']}", json={"title": "Ler 6 livros", "target_value": 6}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Ler 6 livros"
    assert update_response.json()["target_value"] == 6

    delete_response = client.delete(f"/api/goals/{goal['id']}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/goals/{goal['id']}", headers=headers)
    assert missing_response.status_code == 404


def test_progress_reaching_target_marks_goal_completed_and_awards_xp(client, register_user):
    tokens = register_user(email="goals3@example.com")
    headers = _auth_headers(tokens)
    goal = _create_goal(client, headers, target_value=2)

    midway = client.patch(f"/api/goals/{goal['id']}", json={"current_value": 1}, headers=headers)
    assert midway.status_code == 200
    assert midway.json()["status"] == "in_progress"
    assert midway.json()["progress_percent"] == 50.0

    completed = client.patch(f"/api/goals/{goal['id']}", json={"current_value": 2}, headers=headers)
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["progress_percent"] == 100.0

    profile = client.get("/api/gamification/profile", headers=headers)
    assert profile.status_code == 200
    body = profile.json()
    assert body["xp_total"] == 100
    codes = {achievement["code"] for achievement in body["achievements"] if achievement["unlocked"]}
    assert "first_goal" in codes


def test_reapplying_completed_progress_does_not_double_award_xp(client, register_user):
    tokens = register_user(email="goals4@example.com")
    headers = _auth_headers(tokens)
    goal = _create_goal(client, headers, target_value=2)

    client.patch(f"/api/goals/{goal['id']}", json={"current_value": 2}, headers=headers)
    profile_after_first = client.get("/api/gamification/profile", headers=headers).json()
    assert profile_after_first["xp_total"] == 100

    again = client.patch(f"/api/goals/{goal['id']}", json={"current_value": 2}, headers=headers)
    assert again.json()["status"] == "completed"

    profile_after_second = client.get("/api/gamification/profile", headers=headers).json()
    assert profile_after_second["xp_total"] == 100


def test_goal_endpoints_require_authentication(client):
    assert client.get("/api/goals").status_code == 401
    assert client.post("/api/goals", json={"title": "x"}).status_code == 401
