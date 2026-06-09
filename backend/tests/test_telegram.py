from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.telegram_account import TelegramAccount


def _auth_headers(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_pending(db_session, *, chat_id, code, expires_in_minutes=15):
    account = TelegramAccount(
        chat_id=chat_id,
        link_code=code,
        link_code_expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
        is_active=False,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


def test_status_reports_not_linked_for_new_user(client, register_user):
    tokens = register_user(email="telegram1@example.com")
    response = client.get("/api/telegram/status", headers=_auth_headers(tokens))
    assert response.status_code == 200
    assert response.json() == {
        "is_linked": False,
        "linked_at": None,
        "bot_username": settings.telegram_bot_username,
    }


def test_link_account_with_valid_code_succeeds(client, register_user, db_session):
    tokens = register_user(email="telegram2@example.com")
    _create_pending(db_session, chat_id=111222333, code="ABC123")

    response = client.post("/api/telegram/link", json={"code": "abc123"}, headers=_auth_headers(tokens))
    assert response.status_code == 200
    body = response.json()
    assert body["is_linked"] is True
    assert body["linked_at"] is not None

    status_response = client.get("/api/telegram/status", headers=_auth_headers(tokens))
    assert status_response.json()["is_linked"] is True


def test_link_account_with_unknown_code_returns_404(client, register_user):
    tokens = register_user(email="telegram3@example.com")
    response = client.post("/api/telegram/link", json={"code": "NOPE99"}, headers=_auth_headers(tokens))
    assert response.status_code == 404


def test_link_account_with_expired_code_returns_400(client, register_user, db_session):
    tokens = register_user(email="telegram4@example.com")
    _create_pending(db_session, chat_id=444555666, code="OLD123", expires_in_minutes=-30)

    response = client.post("/api/telegram/link", json={"code": "OLD123"}, headers=_auth_headers(tokens))
    assert response.status_code == 400


def test_link_account_replaces_previous_link(client, register_user, db_session):
    tokens = register_user(email="telegram5@example.com")
    _create_pending(db_session, chat_id=1, code="FIRST1")
    client.post("/api/telegram/link", json={"code": "FIRST1"}, headers=_auth_headers(tokens))

    _create_pending(db_session, chat_id=2, code="SECOND")
    response = client.post("/api/telegram/link", json={"code": "SECOND"}, headers=_auth_headers(tokens))
    assert response.status_code == 200
    assert response.json()["is_linked"] is True

    accounts = db_session.query(TelegramAccount).all()
    linked = [a for a in accounts if a.user_id is not None]
    assert len(linked) == 1
    assert linked[0].chat_id == 2


def test_unlink_removes_account(client, register_user, db_session):
    tokens = register_user(email="telegram6@example.com")
    _create_pending(db_session, chat_id=777888999, code="GONE12")
    client.post("/api/telegram/link", json={"code": "GONE12"}, headers=_auth_headers(tokens))

    response = client.delete("/api/telegram/link", headers=_auth_headers(tokens))
    assert response.status_code == 200

    status_response = client.get("/api/telegram/status", headers=_auth_headers(tokens))
    assert status_response.json()["is_linked"] is False


def test_unlink_without_linked_account_returns_404(client, register_user):
    tokens = register_user(email="telegram7@example.com")
    response = client.delete("/api/telegram/link", headers=_auth_headers(tokens))
    assert response.status_code == 404


def test_telegram_endpoints_require_authentication(client):
    assert client.get("/api/telegram/status").status_code == 401


def test_link_and_unlink_commit_the_transaction(client, register_user, db_session, monkeypatch):
    """Each real request gets its own session that's closed (and rolled back if
    uncommitted) once the response is sent — the shared `db_session` fixture
    would let a missing `db.commit()` slip by unnoticed (changes stay visible
    via flush within the same transaction), so spy on `commit` directly to
    enforce that the link survives across requests in production."""
    tokens = register_user(email="telegram8@example.com")
    _create_pending(db_session, chat_id=121212, code="COMMIT")

    commits = []
    monkeypatch.setattr(db_session, "commit", lambda: commits.append(True))

    link_response = client.post("/api/telegram/link", json={"code": "COMMIT"}, headers=_auth_headers(tokens))
    assert link_response.status_code == 200
    assert commits, "linking an account must commit so the change persists beyond the request"

    commits.clear()
    unlink_response = client.delete("/api/telegram/link", headers=_auth_headers(tokens))
    assert unlink_response.status_code == 200
    assert commits, "unlinking an account must commit so the change persists beyond the request"
    assert client.post("/api/telegram/link", json={"code": "ABC123"}).status_code == 401
    assert client.delete("/api/telegram/link").status_code == 401
