def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_task(client, headers, **overrides):
    payload = {
        "title": "Estudar para a prova",
        "description": "Capítulos 3 e 4",
        "priority": "high",
        "due_date": "2026-06-10",
        "due_time": "18:00:00",
        "recurrence": "none",
    }
    payload.update(overrides)
    response = client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_list_tasks(client, register_user):
    tokens = register_user(email="tasks@example.com")
    headers = _auth_headers(tokens)

    created = _create_task(client, headers)
    assert created["status"] == "pending"
    assert created["priority"] == "high"
    assert created["xp_awarded"] == 0

    response = client.get("/api/tasks", headers=headers)
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert "Estudar para a prova" in titles


def test_get_update_and_delete_task(client, register_user):
    tokens = register_user(email="taskcrud@example.com")
    headers = _auth_headers(tokens)
    task = _create_task(client, headers)

    get_response = client.get(f"/api/tasks/{task['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task["id"]

    update_response = client.patch(
        f"/api/tasks/{task['id']}", json={"title": "Estudar para a prova final", "priority": "medium"}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Estudar para a prova final"
    assert update_response.json()["priority"] == "medium"

    delete_response = client.delete(f"/api/tasks/{task['id']}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/tasks/{task['id']}", headers=headers)
    assert missing_response.status_code == 404


def test_complete_task_marks_completed_and_sets_timestamp(client, register_user):
    tokens = register_user(email="taskcomplete@example.com")
    headers = _auth_headers(tokens)
    task = _create_task(client, headers, recurrence="none")

    response = client.post(f"/api/tasks/{task['id']}/complete", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None

    reopened = client.post(f"/api/tasks/{task['id']}/reopen", headers=headers)
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "pending"
    assert reopened.json()["completed_at"] is None


def test_completing_recurring_task_spawns_next_occurrence(client, register_user):
    tokens = register_user(email="taskrecurrence@example.com")
    headers = _auth_headers(tokens)
    task = _create_task(client, headers, due_date="2026-06-10", recurrence="daily")

    response = client.post(f"/api/tasks/{task['id']}/complete", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    list_response = client.get("/api/tasks", headers=headers)
    tasks = list_response.json()
    assert len(tasks) == 2

    next_occurrence = next(t for t in tasks if t["id"] != task["id"])
    assert next_occurrence["status"] == "pending"
    assert next_occurrence["due_date"] == "2026-06-11"
    assert next_occurrence["parent_task_id"] == task["id"]


def test_tasks_are_isolated_per_user(client, register_user):
    tokens_a = register_user(email="usera@example.com")
    tokens_b = register_user(email="userb@example.com")

    task = _create_task(client, _auth_headers(tokens_a))

    forbidden = client.get(f"/api/tasks/{task['id']}", headers=_auth_headers(tokens_b))
    assert forbidden.status_code == 404

    list_b = client.get("/api/tasks", headers=_auth_headers(tokens_b))
    assert list_b.json() == []


def test_tasks_endpoints_require_authentication(client):
    assert client.get("/api/tasks").status_code == 401
    assert client.post("/api/tasks", json={"title": "x"}).status_code == 401
