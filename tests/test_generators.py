from app.modules.generators import (
    generate_campaign_ideas,
    generate_copy_variants,
    generate_landing_page,
    generate_review_checklist,
    generate_static_creative_concepts,
    generate_video_script,
)


def test_campaign_ideas_are_generated():
    brief = {
        "brand": "ExampleBrand",
        "product": "meal kits",
        "audience": "young families",
        "offer": "50% off",
        "goal": "increase sales",
        "channel": "Meta ads",
    }
    ideas = generate_campaign_ideas(brief)
    assert isinstance(ideas, list)
    assert len(ideas) >= 3


def test_copy_variants_are_generated():
    brief = {"brand": "ExampleBrand", "product": "meal kits", "audience": "young families", "offer": "50% off", "cta": "Shop now"}
    copy = generate_copy_variants(brief)
    assert "hooks" in copy
    assert "headlines" in copy
    assert "primary_text" in copy
    assert len(copy["hooks"]) >= 2


def test_video_script_and_creatives_are_generated():
    brief = {"brand": "ExampleBrand", "product": "meal kits", "audience": "young families", "cta": "Shop now"}
    script = generate_video_script(brief)
    assert "script" in script
    assert "ugc_ideas" in script
    assert len(script["script"]) >= 3

    creative = generate_static_creative_concepts(brief)
    assert isinstance(creative, list)
    assert len(creative) >= 3


def test_landing_page_and_review_checklist_are_generated():
    brief = {"brand": "ExampleBrand", "product": "meal kits", "offer": "50% off", "audience": "young families", "cta": "Try now"}
    landing = generate_landing_page(brief)
    assert "hero" in landing
    assert "cta" in landing
    assert landing["hero"] == "Explore meal kits with ExampleBrand"
    assert "review the details of 50% off" in landing["subhead"]
    assert all("better results" not in bullet.lower() for bullet in landing["bullets"])

    checklist = generate_review_checklist(brief)
    assert isinstance(checklist, list)
    assert len(checklist) >= 3
