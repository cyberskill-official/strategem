"""Test helpers for authenticated API calls."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient,
    email: str = "user@example.com",
    password: str = "password123",
    *,
    tier: str | None = None,
) -> dict[str, Any]:
    """Register, optionally bump tier on the in-memory store, return login body."""
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    body = login.json()
    if tier is not None:
        svc = client.app.state.auth_service
        assert svc is not None
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access']}"})
        assert me.status_code == 200, me.text
        from uuid import UUID

        uid = UUID(str(me.json()["user_id"]))
        user = svc.store.get_by_id(uid)
        assert user is not None
        user.tier = tier
        if hasattr(svc.store, "update"):
            svc.store.update(user)
        # Re-login so any claim-based paths see the new tier
        login = client.post("/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        body = login.json()
    return body


def auth_header(access: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access}"}
