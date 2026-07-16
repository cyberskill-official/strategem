"""Onboarding + help center — TASK-EDU-004."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OnboardingStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    body: str
    cta: str = ""


def onboarding_path() -> list[OnboardingStep]:
    return [
        OnboardingStep(
            id="welcome",
            title="Welcome",
            body="Tam Thuc Strategem is decision support, not fortune-telling.",
            cta="Continue",
        ),
        OnboardingStep(
            id="cast",
            title="Cast a chart",
            body="Enter a datetime and question; the engine produces a deterministic la so.",
            cta="Try cast",
        ),
        OnboardingStep(
            id="read",
            title="Read with citations",
            body="AI interpretation always shows disclosure and classical citations.",
            cta="See results",
        ),
        OnboardingStep(
            id="decide",
            title="You decide",
            body="Use chu-khach framing; the tool never issues a verdict.",
            cta="Done",
        ),
    ]


def help_topics() -> list[dict[str, str]]:
    return [
        {"id": "disclaimer", "title": "Disclaimer", "body": "Educational / decision support only."},
        {
            "id": "schools",
            "title": "School flags",
            "body": "Configure co_truong_phai under Manage → Settings.",
        },
        {
            "id": "export",
            "title": "Export",
            "body": "PDF via report export; PNG/SVG via chart export.",
        },
    ]
