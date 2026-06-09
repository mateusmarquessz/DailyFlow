from datetime import date, timedelta

TODAY = date.today()


def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_task(client, headers, **overrides):
    payload = {
        "title": "Tarefa",
        "priority": "medium",
        "due_date": TODAY.isoformat(),
        "recurrence": "none",
    }
    payload.update(overrides)
    response = client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _create_habit(client, headers, **overrides):
    payload = {"name": "Meditar", "frequency": "daily", "color": "#22C55E", "icon": "leaf"}
    payload.update(overrides)
    response = client.post("/api/habits", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _check_in(client, headers, habit_id, on_date):
    response = client.post(
        f"/api/habits/{habit_id}/check-in", json={"on_date": on_date.isoformat()}, headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def _profile(client, headers):
    response = client.get("/api/gamification/profile", headers=headers)
    assert response.status_code == 200
    return response.json()


def test_profile_starts_at_level_one_with_no_unlocked_achievements(client, register_user):
    tokens = register_user(email="gami1@example.com")
    headers = _auth_headers(tokens)

    body = _profile(client, headers)
    assert body["xp_total"] == 0
    assert body["level"] == 1
    assert body["xp_for_next_level"] == 100
    assert len(body["achievements"]) > 0
    assert all(not achievement["unlocked"] for achievement in body["achievements"])


def test_completing_task_awards_xp_and_unlocks_first_task_achievement(client, register_user):
    tokens = register_user(email="gami2@example.com")
    headers = _auth_headers(tokens)
    task = _create_task(client, headers, priority="high")

    response = client.post(f"/api/tasks/{task['id']}/complete", headers=headers)
    assert response.status_code == 200
    assert response.json()["xp_awarded"] == 30

    body = _profile(client, headers)
    assert body["xp_total"] == 30
    unlocked = {a["code"] for a in body["achievements"] if a["unlocked"]}
    assert "first_task" in unlocked


def test_completing_and_reopening_task_does_not_double_award_xp(client, register_user):
    tokens = register_user(email="gami3@example.com")
    headers = _auth_headers(tokens)
    task = _create_task(client, headers, priority="low")

    client.post(f"/api/tasks/{task['id']}/complete", headers=headers)
    assert _profile(client, headers)["xp_total"] == 10

    client.post(f"/api/tasks/{task['id']}/reopen", headers=headers)
    client.post(f"/api/tasks/{task['id']}/complete", headers=headers)

    assert _profile(client, headers)["xp_total"] == 10


def test_completing_enough_tasks_levels_up_and_unlocks_milestone(client, register_user):
    tokens = register_user(email="gami4@example.com")
    headers = _auth_headers(tokens)

    # 4 high-priority tasks (30 XP each) cross the level-1 threshold (100 XP) and reach level 2.
    for index in range(4):
        task = _create_task(client, headers, title=f"Tarefa {index}", priority="high")
        client.post(f"/api/tasks/{task['id']}/complete", headers=headers)

    body = _profile(client, headers)
    assert body["xp_total"] == 120
    assert body["level"] == 2
    unlocked = {a["code"] for a in body["achievements"] if a["unlocked"]}
    assert "first_task" in unlocked
    assert "tasks_10" not in unlocked


def test_habit_checkin_awards_xp_updates_streak_and_unlocks_first_habit(client, register_user):
    tokens = register_user(email="gami5@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers)

    for offset in range(3):
        _check_in(client, headers, habit["id"], TODAY - timedelta(days=offset))

    body = _profile(client, headers)
    assert body["xp_total"] == 45
    assert body["current_streak"] == 3
    assert body["longest_streak"] == 3
    unlocked = {a["code"] for a in body["achievements"] if a["unlocked"]}
    assert "first_habit" in unlocked


def test_repeated_checkin_for_same_day_does_not_double_award_xp(client, register_user):
    tokens = register_user(email="gami6@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers)

    _check_in(client, headers, habit["id"], TODAY)
    _check_in(client, headers, habit["id"], TODAY)

    assert _profile(client, headers)["xp_total"] == 15


def test_gamification_endpoint_requires_authentication(client):
    assert client.get("/api/gamification/profile").status_code == 401
