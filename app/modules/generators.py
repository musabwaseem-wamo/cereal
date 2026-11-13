"""Deterministic mock generators for campaign strategy and creative assets."""

from __future__ import annotations

from typing import Dict, List


def generate_campaign_ideas(brief: Dict[str, str]) -> List[Dict[str, str]]:
    brand = brief.get("brand", "Brand")
    product = brief.get("product", "your product")
    audience = brief.get("audience", "target customers")
    offer = brief.get("offer", "a compelling offer")
    channel = brief.get("channel", "Meta ads")
    cta = brief.get("cta", "Shop now")
    goal = brief.get("goal", "").lower()
    if any(term in goal for term in ("awareness", "reach", "recognition")):
        primary_kpi = "Reach or CPM, with frequency as a guardrail"
    elif any(term in goal for term in ("lead", "sign-up", "signup", "registration")):
        primary_kpi = "Qualified lead rate and cost per qualified lead"
    elif any(term in goal for term in ("sale", "purchase", "conversion", "revenue")):
        primary_kpi = "Purchase conversion rate, CPA and ROAS; CTR as a creative diagnostic"
    elif any(term in goal for term in ("click", "traffic", "visit")):
        primary_kpi = "Outbound CTR and CPC"
    else:
        primary_kpi = f"The primary outcome metric for the stated goal: {brief.get('goal', 'campaign objective')}"

    return [
        {
            "title": "The friction-to-relief story",
            "audience_insight": f"Hypothesis to validate: {audience} encounter a specific recurring friction related to {product}.",
            "strategic_angle": "Make the audience's real-world friction the opening, then show the product as one considered way to address it.",
            "strategic_rationale": "A recognizable tension can earn attention before the brand asks for action; it gives the creative a clear problem-to-solution arc.",
            "core_message": f"{brand} offers an option to consider when addressing the friction around {product}.",
            "creative_execution": f"Create a short vertical story: 1) show the verified friction, 2) reveal {product} in use, 3) state one substantiated benefit, 4) present {offer} and {cta}.",
            "test_hypothesis": f"Against a product-first control, test whether a problem-first opening improves {primary_kpi} on {channel}.",
            "primary_kpi": primary_kpi,
            "evidence_to_confirm": "Confirm the problem reflects real customer language and substantiate any stated benefit; otherwise keep both as hypotheses.",
        },
        {
            "title": "Proof through the product",
            "audience_insight": f"Hypothesis to validate: people evaluating {product} need to understand how it works before taking the next step.",
            "strategic_angle": "Replace broad benefit language with a transparent demonstration of the product experience.",
            "strategic_rationale": "Showing concrete steps can reduce uncertainty and lets viewers judge relevance without relying on unsupported promises.",
            "core_message": f"See how {product} works, what is included and whether it fits your needs.",
            "creative_execution": f"Film a hands-on vertical walkthrough: show the real {product} experience or service entry point, demonstrate two or three actual steps, disclose relevant terms, then finish with {cta}.",
            "test_hypothesis": f"Against a benefit-led control, test whether a step-by-step demonstration improves {primary_kpi}; monitor drop-off as a guardrail.",
            "primary_kpi": primary_kpi,
            "evidence_to_confirm": "Use the actual product, current inclusions and accurate usage steps; avoid implying results that have not been verified.",
        },
        {
            "title": "One product, several use cases",
            "audience_insight": f"Hypothesis to validate: different people in {audience} may see different reasons to consider {product}.",
            "strategic_angle": "Show a small set of distinct, real use cases so the viewer can self-select the one most relevant to them.",
            "strategic_rationale": "A use-case matrix tests audience relevance instead of assuming one universal motivation.",
            "core_message": f"Explore the {product} use case that best matches what you are looking for.",
            "creative_execution": f"Produce three cutdowns with the same visual style but different verified use moments. Keep the product and {offer} constant; change only the use case and its opening line.",
            "test_hypothesis": f"Compare the three use-case openings against one broad control using {primary_kpi}; keep audience, spend and placement consistent.",
            "primary_kpi": primary_kpi,
            "evidence_to_confirm": "Only show options or scenarios genuinely supported by the product; remove any use case that cannot be substantiated.",
        },
        {
            "title": "The offer, without the fine-print surprise",
            "audience_insight": f"Hypothesis to validate: {audience} may hesitate if the value or conditions of {offer} are unclear.",
            "strategic_angle": "Make the offer easy to understand, then give the product enough context to make the value credible.",
            "strategic_rationale": "Clarity can remove avoidable decision friction; stating terms visibly also protects trust and sets accurate expectations.",
            "core_message": f"Understand exactly what {offer} includes and how to take the next step with {brand}.",
            "creative_execution": f"Create an offer-led static and a short video variant. Make the terms legible, show {product} in context, and use {cta} as the single next step.",
            "test_hypothesis": f"Compare offer-first with product-first creative on {primary_kpi}, while checking for offer-related bounce or low-quality actions.",
            "primary_kpi": primary_kpi,
            "evidence_to_confirm": f"Verify eligibility, exclusions, dates and availability for {offer}; include material conditions in readable copy.",
        },
        {
            "title": "The question worth answering",
            "audience_insight": f"Hypothesis to validate: an unanswered practical question about {product} creates hesitation for some {audience}.",
            "strategic_angle": "Turn one verified customer question into a useful, direct response instead of leaning on generic urgency.",
            "strategic_rationale": "An objection-led message can make the campaign more helpful and reveal what information is missing from the buying journey.",
            "core_message": f"Get a clear, factual answer about {product} before deciding whether to {cta.lower()}.",
            "creative_execution": f"Ask one real FAQ on screen, answer it with approved facts in a direct-to-camera or caption-led video, show the relevant part of {product}, and close with {cta}.",
            "test_hypothesis": f"Compare the FAQ response with a general product introduction on {primary_kpi}; track FAQ engagement as a diagnostic, not the success outcome.",
            "primary_kpi": primary_kpi,
            "evidence_to_confirm": "Select the question from actual support or sales feedback and have the answer reviewed by the product or legal owner.",
        },
    ]


def generate_copy_variants(brief: Dict[str, str], selected_idea: str | None = None) -> Dict[str, List[str]]:
    brand = brief.get("brand", "Brand")
    product = brief.get("product", "your product")
    audience = brief.get("audience", "busy shoppers")
    offer = brief.get("offer", "a limited-time offer")
    cta = brief.get("cta", "Shop now")
    idea_context = f" based on this campaign idea: {selected_idea}" if selected_idea else ""

    hooks = [
        f"Considering {product}? See what {brand} includes before deciding.{idea_context}",
        f"Explore how {brand} approaches {product} for {audience}.{idea_context}",
        f"Looking for a clear way to compare {product}? Start with the details.{idea_context}",
    ]

    headlines = [
        f"Explore {product} with {brand}",
        f"See the details on {offer}",
        f"Made for {audience}",
        f"Discover how {product} works",
    ]

    primary_text = [
        f"Explore how {brand} approaches {product} for {audience}. Review what is included, how it works, and whether it fits your needs.",
        f"Take a closer look at {offer}, including the terms and details that matter. Then decide whether {brand} is right for you.",
        f"See what is included in {product}, compare the details, and choose your next step with {brand}.",
    ]

    return {"hooks": hooks, "headlines": headlines, "primary_text": primary_text, "cta": [cta]}


def generate_static_creative_concepts(brief: Dict[str, str]) -> List[str]:
    brand = brief.get("brand", "Brand")
    product = brief.get("product", "product")
    offer = brief.get("offer", "special offer")
    tone = brief.get("tone", "confident and modern")

    return [
        f"Split-screen concept: a realistic moment involving {product} on one side and a clear product detail on the other; leave space for reviewed copy.",
        f"Close-up lifestyle photograph featuring {product}, with a clean premium layout and a {tone} visual mood.",
        f"Three-panel story for {product}: context, product in use, and a relevant detail; avoid implying an unverified outcome.",
        f"Minimal product hero for {brand}: accurate product representation, strong contrast, and clear negative space for optional offer copy.",
    ]


def generate_video_script(
    brief: Dict[str, str],
    duration_seconds: int = 30,
    selected_idea: Dict[str, str] | None = None,
) -> Dict[str, List[Dict[str, str | int]] | List[str] | int]:
    brand = brief.get("brand", "Brand")
    product = brief.get("product", "product")
    audience = brief.get("audience", "your audience")
    cta = brief.get("cta", "Shop now")

    duration_seconds = max(15, min(duration_seconds, 60))
    beats = [
        (0.12, "Opening hook", f"Show a recognizable moment from the day of {audience}."),
        (0.24, "The situation", f"Show the everyday context or question that makes {product} relevant."),
        (0.24, "Product demonstration", f"Show how {brand} or {product} works using only verified details."),
        (0.20, "Why consider it", "Show the product detail that supports the message; use approved evidence if available."),
        (0.20, "Offer and call to action", f"State {brief.get('offer', 'the offer')} clearly and end with “{cta}”."),
    ]
    voiceovers = [
        f"Looking for a new way to approach {product}?",
        "Think about what matters most in your day-to-day routine.",
        f"Here is a closer look at {product} from {brand}.",
        "Explore the details and see whether it fits what you need.",
        f"{brief.get('offer', 'Explore the offer')}. {cta}.",
    ]
    scenes: list[dict[str, str | int]] = []
    start = 0
    for index, (share, beat, visual) in enumerate(beats):
        end = duration_seconds if index == len(beats) - 1 else min(
            duration_seconds, start + max(2, round(duration_seconds * share))
        )
        if end <= start:
            continue
        if selected_idea and index == 2:
            visual = selected_idea["creative_execution"]
        scenes.append({
            "start_seconds": start,
            "end_seconds": end,
            "beat": beat,
            "visual": visual,
            "voiceover": voiceovers[index],
            "on_screen_text": brief.get("offer", "") if index == len(beats) - 1 else "",
        })
        start = end

    ugc_ideas = [
        f"UGC concept 1: a paid creator demonstrates verified {product} details for {audience}; use no invented personal testimonial.",
        f"UGC concept 2: a day-in-the-life placement showing {product} in a realistic, brief-supported use case; avoid unverified results.",
        f"UGC concept 3: a creator answers a real question using approved facts, then gives the viewer the {cta.lower()} next step.",
    ]

    return {"duration_seconds": duration_seconds, "script": scenes, "ugc_ideas": ugc_ideas}


def generate_landing_page(brief: Dict[str, str]) -> Dict[str, str]:
    brand = brief.get("brand", "Brand")
    product = brief.get("product", "your product")
    offer = brief.get("offer", "special offer")
    audience = brief.get("audience", "your audience")
    cta = brief.get("cta", "Get started")

    return {
        "hero": f"Explore {product} with {brand}",
        "subhead": f"See what is included, review the details of {offer}, and decide whether it is right for you.",
        "cta": cta,
        "bullets": [
            f"Explore the details of {product}",
            f"Review {offer} before deciding",
            f"Choose whether to continue with {brand}",
        ],
    }


def generate_review_checklist(brief: Dict[str, str]) -> List[str]:
    return [
        "Validate that the angle matches the brand tone and campaign objective.",
        "Check for factual accuracy, legal compliance and offer clarity.",
        "Review audience fit to ensure the creative speaks directly to the target customer.",
        "Ensure the CTA is visible, honest and consistent with the landing page.",
        "Confirm the content would still work when tested across channels and placements.",
    ]
