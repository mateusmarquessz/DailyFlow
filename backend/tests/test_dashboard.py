from datetime import date

TODAY = date.today()


def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_dashboard_stats_aggregate_tasks_and_habits(client, register_user):
    tokens = register_user(email="dashboard@example.com")
    headers = _auth_headers(tokens)

    due_today = client.post(
        "/api/tasks",
        json={"title": "Tarefa de hoje", "due_date": TODAY.isoformat(), "recurrence": "none"},
        headers=headers,
    ).json()
    client.post(f"/api/tasks/{due_today['id']}/complete", headers=headers)

    client.post(
        "/api/tasks",
        json={"title": "Tarefa pendente de hoje", "due_date": TODAY.isoformat(), "recurrence": "none"},
        headers=headers,
    )
    client.post("/api/tasks", json={"title": "Tarefa sem data", "recurrence": "none"}, headers=headers)

    habit = client.post(
        "/api/habits", json={"name": "Meditar", "frequency": "daily", "color": "#6366F1", "icon": "brain"}, headers=headers
    ).json()
    client.post(f"/api/habits/{habit['id']}/check-in", json={"on_date": TODAY.isoformat()}, headers=headers)
    client.post("/api/habits", json={"name": "Ler", "frequency": "daily", "color": "#22C55E", "icon": "book-open"}, headers=headers)

    client.post("/api/goals", json={"title": "Meta ativa", "type": "monthly", "target_value": 4}, headers=headers)
    completed_goal = client.post(
        "/api/goals", json={"title": "Meta concluída", "type": "weekly", "target_value": 1}, headers=headers
    ).json()
    client.patch(f"/api/goals/{completed_goal['id']}", json={"current_value": 1}, headers=headers)

    response = client.get("/api/dashboard/stats", headers=headers)
    assert response.status_code == 200
    body = response.json()

    assert body["tasks_due_today"] == 2
    assert body["tasks_completed_today"] == 1
    assert body["habits_total"] == 2
    assert body["habits_completed_today"] == 1
    assert body["best_current_streak"] == 1
    assert body["goals_in_progress"] == 1

    assert len(body["weekly_completions"]) == 7
    today_entry = next(entry for entry in body["weekly_completions"] if entry["date"] == TODAY.isoformat())
    assert today_entry["tasks_completed"] == 1
    assert today_entry["habits_completed"] == 1


def test_dashboard_stats_with_no_data_returns_zeros(client, register_user):
    tokens = register_user(email="dashboardempty@example.com")
    headers = _auth_headers(tokens)

    response = client.get("/api/dashboard/stats", headers=headers)
    assert response.status_code == 200
    body = response.json()

    assert body["tasks_due_today"] == 0
    assert body["tasks_completed_today"] == 0
    assert body["habits_total"] == 0
    assert body["habits_completed_today"] == 0
    assert body["best_current_streak"] == 0
    assert all(entry["tasks_completed"] == 0 and entry["habits_completed"] == 0 for entry in body["weekly_completions"])


def test_dashboard_endpoint_requires_authentication(client):
    assert client.get("/api/dashboard/stats").status_code == 401
