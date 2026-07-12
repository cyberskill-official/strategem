from __future__ import annotations

from tamthuc_rag.review.models import AuditRow, ReviewTicket


class ReviewQueue:
    def __init__(self) -> None:
        self.tickets: dict[str, ReviewTicket] = {}
        self.audit: list[AuditRow] = []

    def enqueue(self, ticket: ReviewTicket) -> ReviewTicket:
        self.tickets[ticket.ticket_id] = ticket
        return ticket

    def get(self, ticket_id: str) -> ReviewTicket | None:
        return self.tickets.get(ticket_id)
