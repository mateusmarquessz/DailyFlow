from datetime import date, timedelta

TODAY = date.today()


def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_habit(client, headers, **overrides):
    payload = {
        "name": "Beber 2L de água",
        "description": "Manter hidratação ao longo do dia",
        "frequency": "daily",
        "color": "#22C55E",
        "icon": "droplet",
    }
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


def _scheduled_days_up_to(reference, target_days, count):
    """Returns the `count` most recent days on/before `reference` whose weekday is in `target_days`, oldest first."""
    days = []
    cursor = reference
    while len(days) < count:
        if cursor.weekday() in target_days:
            days.append(cursor)
        cursor -= timedelta(days=1)
    return list(reversed(days))


def test_create_and_list_habits(client, register_user):
    tokens = register_user(email="habits@example.com")
    headers = _auth_headers(tokens)

    created = _create_habit(client, headers)
    assert created["current_streak"] == 0
    assert created["longest_streak"] == 0
    assert created["completed_today"] is False

    response = client.get("/api/habits", headers=headers)
    assert response.status_code == 200
    names = [habit["name"] for habit in response.json()]
    assert "Beber 2L de água" in names


def test_check_in_builds_consecutive_streak(client, register_user):
    tokens = register_user(email="habitstreak@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers, frequency="daily")

    for offset in (2, 1, 0):
        result = _check_in(client, headers, habit["id"], TODAY - timedelta(days=offset))

    assert result["current_streak"] == 3
    assert result["longest_streak"] == 3
    assert result["completed_today"] is True

    history_response = client.get(f"/api/habits/{habit['id']}/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 3
    assert all(entry["completed"] for entry in history)
    assert history[-1]["streak_snapshot"] == 3


def test_breaking_streak_resets_current_but_keeps_longest(client, register_user):
    tokens = register_user(email="habitbreak@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers, frequency="daily")

    # Build a 3-day streak ending 5 days ago, then a fresh 1-day streak today —
    # leaving a gap so the historic run becomes the longest while the current run is shorter.
    for offset in (7, 6, 5):
        _check_in(client, headers, habit["id"], TODAY - timedelta(days=offset))
    result = _check_in(client, headers, habit["id"], TODAY)

    assert result["longest_streak"] == 3
    assert result["current_streak"] == 1


def test_remove_check_in_undoes_completion(client, register_user):
    tokens = register_user(email="habitundo@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers, frequency="daily")

    _check_in(client, headers, habit["id"], TODAY)
    undo = client.delete(
        f"/api/habits/{habit['id']}/check-in",
        params={"on_date": TODAY.isoformat()},
        headers=headers,
    )
    assert undo.status_code == 200
    assert undo.json()["current_streak"] == 0

    history_response = client.get(f"/api/habits/{habit['id']}/history", headers=headers)
    assert history_response.json() == []


def test_weekly_habit_streak_only_counts_target_days(client, register_user):
    tokens = register_user(email="habitweekly@example.com")
    headers = _auth_headers(tokens)
    target_days = [0, 2, 4]  # segunda, quarta, sexta
    habit = _create_habit(client, headers, name="Academia", frequency="weekly", target_days=target_days)

    days = _scheduled_days_up_to(TODAY, target_days, 3)
    result = None
    for day in days:
        result = _check_in(client, headers, habit["id"], day)

    assert result["current_streak"] == 3
    assert result["longest_streak"] == 3


def test_update_and_delete_habit(client, register_user):
    tokens = register_user(email="habitcrud@example.com")
    headers = _auth_headers(tokens)
    habit = _create_habit(client, headers)

    update_response = client.patch(
        f"/api/habits/{habit['id']}", json={"name": "Beber 3L de água", "is_active": False}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Beber 3L de água"
    assert update_response.json()["is_active"] is False

    delete_response = client.delete(f"/api/habits/{habit['id']}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/habits/{habit['id']}", headers=headers)
    assert missing_response.status_code == 404


def test_habits_endpoints_require_authentication(client):
    assert client.get("/api/habits").status_code == 401
    assert client.post("/api/habits", json={"name": "x"}).status_code == 401
