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
            body=(
                "Tam Thuc Strategem sits with you while you think — heritage education "
                "and a kind place to lean, never fortune-telling."
            ),
            cta="Continue",
        ),
        OnboardingStep(
            id="cast",
            title="Draw a picture",
            body=(
                "Bring a datetime and an honest question. The engine draws a "
                "reproducible classical picture you can look at slowly."
            ),
            cta="Try once",
        ),
        OnboardingStep(
            id="read",
            title="Read with sources",
            body=(
                "Suggestions always show AI disclosure and classical citations — "
                "a place to lean, not a destiny claim."
            ),
            cta="See results",
        ),
        OnboardingStep(
            id="decide",
            title="You decide",
            body=(
                "Use host–guest framing to think clearly. The tool never issues a "
                "verdict — kindness and judgment stay with you."
            ),
            cta="Done",
        ),
    ]


def help_topics() -> list[dict[str, str]]:
    return [
        {
            "id": "disclaimer",
            "title": "Disclaimer",
            "body": (
                "Heritage education and decision support only — not fortune-telling, "
                "not medical, legal, or financial advice."
            ),
        },
        {
            "id": "schools",
            "title": "School flags",
            "body": "Choose school methods under Manage → Settings. No school is labeled right or wrong.",
        },
        {
            "id": "export",
            "title": "Export",
            "body": "PDF via the reading export; PNG/SVG via chart export.",
        },
    ]
