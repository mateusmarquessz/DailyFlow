from datetime import date, timedelta

TODAY = date.today()


def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _build_scenario(client, headers):
    in_period_done = client.post(
        "/api/tasks",
        json={"title": "Tarefa concluída", "due_date": TODAY.isoformat(), "recurrence": "none"},
        headers=headers,
    ).json()
    client.post(f"/api/tasks/{in_period_done['id']}/complete", headers=headers)

    client.post(
        "/api/tasks",
        json={"title": "Tarefa pendente", "due_date": TODAY.isoformat(), "recurrence": "none"},
        headers=headers,
    )

    out_of_range = TODAY - timedelta(days=60)
    client.post(
        "/api/tasks",
        json={"title": "Tarefa antiga", "due_date": out_of_range.isoformat(), "recurrence": "none"},
        headers=headers,
    )

    habit = client.post(
        "/api/habits",
        json={"name": "Meditar", "frequency": "daily", "color": "#6366F1", "icon": "brain"},
        headers=headers,
    ).json()
    client.post(f"/api/habits/{habit['id']}/check-in", json={"on_date": TODAY.isoformat()}, headers=headers)

    goal = client.post(
        "/api/goals", json={"title": "Meta da semana", "type": "weekly", "target_value": 1}, headers=headers
    ).json()
    client.patch(f"/api/goals/{goal['id']}", json={"current_value": 1}, headers=headers)


def test_weekly_summary_aggregates_period_data(client, register_user):
    tokens = register_user(email="reports1@example.com")
    headers = _auth_headers(tokens)
    _build_scenario(client, headers)

    response = client.get(
        "/api/reports/summary",
        params={"period": "weekly", "reference_date": TODAY.isoformat()},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert body["period"] == "weekly"
    assert body["start_date"] == (TODAY - timedelta(days=6)).isoformat()
    assert body["end_date"] == TODAY.isoformat()
    assert len(body["daily_breakdown"]) == 7

    assert body["tasks_completed"] == 1
    assert body["tasks_due"] == 2
    assert body["task_completion_rate"] == 50.0
    assert body["habits_active"] == 1
    assert body["habit_checkins"] == 1
    assert body["habit_completion_rate"] > 0
    assert body["goals_completed"] == 1
    assert body["best_streak"] == 1

    today_entry = next(entry for entry in body["daily_breakdown"] if entry["date"] == TODAY.isoformat())
    assert today_entry["tasks_completed"] == 1
    assert today_entry["habits_completed"] == 1


def test_daily_and_monthly_periods_have_expected_ranges(client, register_user):
    tokens = register_user(email="reports2@example.com")
    headers = _auth_headers(tokens)

    daily = client.get(
        "/api/reports/summary", params={"period": "daily", "reference_date": TODAY.isoformat()}, headers=headers
    ).json()
    assert daily["start_date"] == daily["end_date"] == TODAY.isoformat()
    assert len(daily["daily_breakdown"]) == 1

    monthly = client.get(
        "/api/reports/summary", params={"period": "monthly", "reference_date": TODAY.isoformat()}, headers=headers
    ).json()
    assert monthly["start_date"] == (TODAY - timedelta(days=29)).isoformat()
    assert len(monthly["daily_breakdown"]) == 30


def test_summary_with_no_data_returns_zeros(client, register_user):
    tokens = register_user(email="reports3@example.com")
    headers = _auth_headers(tokens)

    response = client.get("/api/reports/summary", params={"period": "weekly"}, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["tasks_completed"] == 0
    assert body["tasks_due"] == 0
    assert body["task_completion_rate"] == 0
    assert body["habits_active"] == 0
    assert body["habit_completion_rate"] == 0
    assert body["goals_completed"] == 0
    assert body["best_streak"] == 0


def test_export_pdf_returns_pdf_document(client, register_user):
    tokens = register_user(email="reports4@example.com")
    headers = _auth_headers(tokens)
    _build_scenario(client, headers)

    response = client.get(
        "/api/reports/export",
        params={"period": "weekly", "format": "pdf", "reference_date": TODAY.isoformat()},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_export_excel_returns_xlsx_document(client, register_user):
    tokens = register_user(email="reports5@example.com")
    headers = _auth_headers(tokens)
    _build_scenario(client, headers)

    response = client.get(
        "/api/reports/export",
        params={"period": "monthly", "format": "excel", "reference_date": TODAY.isoformat()},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")


def test_reports_require_authentication(client):
    summary_response = client.get("/api/reports/summary")
    assert summary_response.status_code == 401

    export_response = client.get("/api/reports/export", params={"format": "pdf"})
    assert export_response.status_code == 401
