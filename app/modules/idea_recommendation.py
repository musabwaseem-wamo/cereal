"""Choose one campaign idea as a transparent, objective-based starting point."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


_OBJECTIVE_SIGNALS = {
    "awareness": (
        ("use cases", "several", "multiple", "variety", "reach", "recognition", "broad"),
        "This direction explores multiple ways the offer may be relevant, making it a useful awareness-test starting point.",
    ),
    "leads": (
        ("proof", "demonstration", "how it works", "question", "faq", "answer", "details", "qualify"),
        "This direction makes the product or decision details clearer, a useful starting point for testing qualified interest.",
    ),
    "traffic": (
        ("friction", "opening", "hook", "problem", "use case", "attention", "visit"),
        "This direction gives the ad a clear opening and reason to visit, a useful starting point for a traffic test.",
    ),
    "sales": (
        ("offer", "terms", "value", "purchase", "conversion", "price", "checkout", "decision"),
        "This direction foregrounds offer or decision clarity, a useful starting point for a purchase-focused test.",
    ),
    "general": (
        ("proof", "demonstration", "how it works", "details", "product"),
        "This direction explains the product clearly, making it a practical starting point to test against the other concepts.",
    ),
}


def recommend_campaign_idea(
    ideas: Sequence[Mapping[str, object]],
    goal: str,
) -> tuple[int, str]:
    """Return a zero-based recommendation and a rationale, without claiming outcome prediction."""
    if not ideas:
        raise ValueError("At least one campaign idea is required to make a recommendation.")

    normalized_goal = goal.casefold()
    if any(term in normalized_goal for term in ("awareness", "reach", "recognition")):
        objective = "awareness"
    elif any(term in normalized_goal for term in ("lead", "sign-up", "signup", "registration")):
        objective = "leads"
    elif any(term in normalized_goal for term in ("sale", "purchase", "conversion", "revenue")):
        objective = "sales"
    elif any(term in normalized_goal for term in ("click", "traffic", "visit")):
        objective = "traffic"
    else:
        objective = "general"

    signals, rationale = _OBJECTIVE_SIGNALS[objective]
    weights = {
        "title": 3,
        "strategic_angle": 2,
        "strategic_rationale": 1,
        "creative_execution": 1,
        "core_message": 1,
    }

    def score(idea: Mapping[str, object]) -> int:
        total = 0
        for field, weight in weights.items():
            value = idea.get(field, "")
            if isinstance(value, str):
                text = value.casefold()
                total += weight * sum(text.count(signal) for signal in signals)
        return total

    best_index = max(range(len(ideas)), key=lambda index: (score(ideas[index]), -index))
    return best_index, rationale
