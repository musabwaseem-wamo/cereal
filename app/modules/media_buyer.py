"""Rule-based media planning for a campaign brief, separate from reporting."""

from __future__ import annotations

from typing import Any


def build_media_plan(
    brief: dict[str, str],
    daily_budget: float,
    selected_idea: dict[str, str] | None = None,
) -> dict[str, Any]:
    goal = brief["goal"].lower()
    if any(term in goal for term in ("awareness", "reach", "recognition")):
        allocations = [
            ("Prospecting reach", 0.65, "Reach and frequency"),
            ("Creative test reserve", 0.25, "Cost per qualified visit"),
            ("Learning reserve", 0.10, "Audience and placement signal"),
        ]
        primary_kpi = "Unique reach or CPM, with frequency as a guardrail"
    elif any(term in goal for term in ("lead", "sign-up", "signup", "registration")):
        allocations = [
            ("Prospecting", 0.60, "Cost per qualified lead"),
            ("Retargeting", 0.25, "Qualified lead rate"),
            ("Creative test reserve", 0.15, "Cost per qualified lead"),
        ]
        primary_kpi = "Qualified leads and cost per qualified lead"
    elif any(term in goal for term in ("click", "traffic", "visit")):
        allocations = [
            ("Prospecting traffic", 0.65, "Outbound CTR and CPC"),
            ("Landing-page test reserve", 0.25, "Qualified landing-page visits"),
            ("Creative test reserve", 0.10, "Outbound CTR and CPC"),
        ]
        primary_kpi = "Qualified landing-page visits and outbound CPC"
    else:
        allocations = [
            ("Prospecting", 0.60, "Purchase conversion rate and CPA"),
            ("Retargeting", 0.25, "Purchase conversion rate and CPA"),
            ("Creative test reserve", 0.15, "CPA and ROAS after sufficient volume"),
        ]
        primary_kpi = "CPA or purchase conversion rate; use ROAS when revenue data is reliable"

    split = []
    allocated_total = 0.0
    for index, (name, share, metric) in enumerate(allocations):
        amount = (
            round(daily_budget - allocated_total, 2)
            if index == len(allocations) - 1
            else round(daily_budget * share, 2)
        )
        allocated_total += amount
        split.append({
            "name": name,
            "share_percent": round(share * 100),
            "daily_budget": amount,
            "success_metric": metric,
        })

    concept = selected_idea["title"] if selected_idea else "the leading concept after human review"
    return {
        "source": "Rule-based planning assistant",
        "daily_budget": round(daily_budget, 2),
        "primary_kpi": primary_kpi,
        "concept": concept,
        "allocations": split,
        "actions": [
            f"Test '{concept}' against a control while keeping audience, placement and offer stable.",
            f"Review {primary_kpi.lower()} only after the agreed learning window and minimum volume.",
            "Move budget in measured steps when results are consistent; preserve a holdout for new creative.",
        ],
        "guardrails": [
            "Planning only: no ad account is connected and no campaign settings are changed.",
            "Confirm budget, audience size, tracking, attribution window and offer terms before launch.",
            "Do not scale from early click-through rate alone when the goal is leads or purchases.",
        ],
    }
