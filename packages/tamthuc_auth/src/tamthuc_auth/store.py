"""User persistence protocol + in-memory implementation for unit tests."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID, uuid4

from tamthuc_auth.errors import ConflictError
from tamthuc_auth.models import UserRecord

log = logging.getLogger("tamthuc_auth.store")


class UserStore(Protocol):
    def create(self, user: UserRecord) -> UserRecord: ...
    def get_by_id(self, user_id: UUID) -> UserRecord | None: ...
    def get_by_email(self, email: str) -> UserRecord | None: ...
    def update(self, user: UserRecord) -> UserRecord: ...


class InMemoryUserStore:
    def __init__(self) -> None:
        self._by_id: dict[UUID, UserRecord] = {}
        self._by_email: dict[str, UUID] = {}

    def create(self, user: UserRecord) -> UserRecord:
        key = user.email.lower()
        if key in self._by_email:
            raise ConflictError("email already registered")
        self._by_id[user.id] = user
        self._by_email[key] = user.id
        log.info("user.created", extra={"user_id": str(user.id)})
        return user

    def get_by_id(self, user_id: UUID) -> UserRecord | None:
        return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> UserRecord | None:
        uid = self._by_email.get(email.lower())
        return self._by_id.get(uid) if uid else None

    def update(self, user: UserRecord) -> UserRecord:
        if user.id not in self._by_id:
            raise KeyError(user.id)
        self._by_id[user.id] = user
        self._by_email[user.email.lower()] = user.id
        return user

    def clear(self) -> None:
        self._by_id.clear()
        self._by_email.clear()


def new_user(
    email: str,
    *,
    password_hash: str | None = None,
    birth_data_envelope: dict[str, Any] | None = None,
    email_verified: bool = False,
    tier: str = "free",
    social_provider: str | None = None,
    social_subject: str | None = None,
    preferences: dict[str, Any] | None = None,
) -> UserRecord:
    now = datetime.now(UTC)
    return UserRecord(
        id=uuid4(),
        email=email.lower(),
        password_hash=password_hash,
        birth_data_envelope=birth_data_envelope,
        preferences=preferences or {},
        email_verified=email_verified,
        tier=tier,
        created_at=now,
        updated_at=now,
        social_provider=social_provider,
        social_subject=social_subject,
    )
