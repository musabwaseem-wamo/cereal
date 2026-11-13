import json
from types import SimpleNamespace

from app import main
from app.modules import llm_service
from app.modules.generators import generate_campaign_ideas as generate_local_ideas
from app.modules.idea_recommendation import recommend_campaign_idea


BRIEF = {
    "brand": "Example Brand",
    "product": "meal kits",
    "audience": "young families",
    "offer": "20% off",
    "goal": "increase sales",
    "channel": "Meta ads",
    "cta": "Shop now",
    "tone": "friendly",
    "constraints": "Avoid unsupported claims",
}

IDEA_FIELDS = (
    "title",
    "audience_insight",
    "strategic_angle",
    "strategic_rationale",
    "core_message",
    "creative_execution",
    "test_hypothesis",
    "primary_kpi",
    "evidence_to_confirm",
)


def make_idea(title):
    return {
        "title": title,
        "audience_insight": "A test audience observation.",
        "strategic_angle": "A distinct strategic direction.",
        "strategic_rationale": "This tests a meaningful audience motivation.",
        "core_message": "One clear takeaway for the audience.",
        "creative_execution": "A practical visual demonstration.",
        "test_hypothesis": "Compare this direction with a control.",
        "primary_kpi": "Purchase conversion rate and CPA",
        "evidence_to_confirm": "Verify product details and offer terms.",
    }


def test_home_serves_local_campaign_studio():
    response = main.app.test_client().get("/")

    assert response.status_code == 200
    assert b"Campaign studio" in response.data
    assert b"styles.css" in response.data
    assert b"Select one campaign idea" in response.data
    assert b"Recommended starting point" in response.data
    assert b"copy-progress" in response.data
    assert b"Total video duration" in response.data
    assert b"Generate / regenerate script" in response.data
    assert b'id="edit-video-upload"' in response.data
    assert b'id="edit-video-preview"' in response.data
    assert b'id="preview-edit-timeline"' in response.data
    assert b"required aria-required=\"true\"" in response.data
    assert b"three sampled still frames are sent to the configured AI" in response.data
    assert b"the full video stays in this browser" in response.data
    assert b'id="edit-visual-analysis-summary"' in response.data
    for workflow in (
        b"AI Idea Generator",
        b"AI Copywriting",
        b"AI Static Creative",
        b"AI Script Writing",
        b"AI UGC Video",
        b"AI Video Editing",
        b"AI Media Buyer",
        b"AI Landing Pages",
        b"Toast / Meta Ads Analysis",
    ):
        assert workflow in response.data
    assert b"id=\"approval-button\"" in response.data
    assert b"id=\"approval-review-dialog\"" in response.data
    assert b"id=\"approval-review-list\"" in response.data
    assert b"id=\"confirm-approval-button\"" in response.data
    assert b"id=\"start-new-campaign\"" in response.data
    assert b"approval-checklist" not in response.data
    assert b"Approve draft" in response.data
    assert b"id=\"open-approved-drafts\"" in response.data
    assert b"id=\"approved-drafts-dialog\"" in response.data
    assert b"id=\"approved-drafts-list\"" in response.data
    assert b"id=\"open-approved-drafts-nav\"" in response.data
    assert b"id=\"approved-drafts-nav-count\"" in response.data
    assert b"id=\"rail-toggle\"" in response.data
    assert b"aria-label=\"Expand sidebar\"" in response.data
    assert b'class="rail-label">AI Idea Generator</span>' in response.data
    assert b"id=\"meta-connect-button\"" in response.data
    assert b"Connect to Meta" in response.data
    assert b"Demo data loaded" in response.data
    assert b"not connected to Meta" in response.data
    assert b"download-landing-button" in response.data
    assert b"Download landing page" in response.data
    assert b"landing-cta-url" not in response.data
    assert b"journey-strip" not in response.data
    assert b"Campaign details" in response.data
    assert b"campaign-generation-status" in response.data
    assert b"edit-suggestions-panel" in response.data
    assert b"START WITH THE ESSENTIALS" not in response.data
    page = response.get_data(as_text=True)
    tab_bar = page.split('<nav class="tabs"', 1)[1].split("</nav>", 1)[0]
    rail = page.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    workflow_tabs = (
        'data-view="overview"',
        'data-view="ideas"',
        'data-view="copy"',
        'data-view="landing"',
        'data-view="creative"',
        'data-view="script"',
        'data-view="ugc"',
        'data-view="editing"',
        'data-view="media"',
        'data-view="ads"',
        'data-view="review"',
    )
    assert [tab_bar.index(tab) for tab in workflow_tabs] == sorted(
        tab_bar.index(tab) for tab in workflow_tabs
    )
    for label in (
        "AI Idea Generator",
        "AI Copywriting",
        "AI Landing Pages",
        "AI Static Creative",
        "AI Script Writing",
        "AI UGC Video",
        "AI Video Editing",
        "AI Media Buyer",
        "Toast / Meta Ads Analysis",
        "Review checklist",
    ):
        assert label in tab_bar
    styles = main.app.test_client().get("/static/styles.css").get_data(as_text=True)
    assert ".tabs{display:grid;grid-template-columns:repeat(11,minmax(0,1fr))" in styles
    assert ".tabs .tab {\n  padding: 10px 5px 10px;" in styles
    assert "font-size: 11px;" in styles
    assert "overflow-x:auto" not in styles.split(".tabs{", 1)[1].split("}", 1)[0]
    assert ".app-shell.sidebar-expanded .rail {\n  width: 236px;" in styles
    assert ".app-shell.sidebar-expanded .main-content {\n  margin-left: 236px;" in styles
    rail_workflow = workflow_tabs[:-1]
    assert [rail.index(tab) for tab in rail_workflow] == sorted(
        rail.index(tab) for tab in rail_workflow
    )
    script = main.app.test_client().get("/static/app.js").get_data(as_text=True)
    assert 'appShell.classList.toggle("sidebar-expanded")' in script
    assert 'railToggle.setAttribute("aria-expanded", String(expanded))' in script
    assert "cerealbox-approved-drafts-v1" in script
    assert "localStorage.setItem" in script
    assert "renderApprovedDrafts" in script
    assert "loadApprovedDraftForEditing" in script
    assert "function startNewCampaign()" in script
    assert 'document.querySelector("#generated-content").classList.add("hidden")' in script
    assert "Your approved campaign is saved in Approved drafts." in script
    assert "Save changes & approve" in script
    assert "function playEditPreview(index, sequence)" in script
    assert "function handleEditVideoUpload()" in script
    assert "async function extractThreeEditFrames()" in script
    assert "function renderEditSuggestions(suggestions)" in script
    assert "campaign-generation-status" in script
    assert "frames," in script
    assert "URL.createObjectURL(file)" in script
    assert "URL.revokeObjectURL(editVideoObjectUrl)" in script
    assert 'editVideoPreview.addEventListener("timeupdate", advanceEditPreview)' in script
    assert "const requiredCampaignSteps = [" in script
    for step in ("ideas", "copy", "landing", "creative", "script", "ugc", "editing", "media"):
        assert f'["{step}",' in script
    assert "confirmButton.disabled = missingSteps.length > 0 || briefChanged" in script
    assert "completedSteps: [...completedCampaignSteps]" in script
    assert "function updateApprovalAvailability()" in script
    assert 'document.querySelector("#approval-review-dialog").close()' in script
    assert 'approvalReviewDialog.showModal()' in script
    assert "Complete all required campaign-building steps before approving." in script
    assert 'document.querySelector("#confirm-approval-button")' in script
    assert 'status.textContent = complete ? "Complete" : "Incomplete"' in script
    assert "function markCurrentDraftModified()" in script
    assert "open-approved-drafts-nav" in script
    assert "workflowOrder" in script
    assert '["overview", "Campaign overview"]' not in script
    assert '["review", "Human review"]' not in script
    assert 'STEP ${String(index + 1).padStart(2, "0")} / ${String(workflowOrder.length).padStart(2, "0")}' in script
    assert "Continue to ${workflowOrder[index + 1][1]}" in script
    assert b"Five distinct strategic territories" in response.data
    assert b"generate-image-prompt-button" in response.data
    assert b"Build image prompt" in response.data
    assert b"image-aspect-ratio" in response.data
    assert b"Copy prompt" in response.data
    for area in (
        b"IDEA GENERATOR",
        b"AI COPYWRITING",
        b"STATIC CREATIVE",
        b"SCRIPT WRITING",
        b"UGC VIDEO",
        b"VIDEO EDITING",
        b"MEDIA BUYER AGENT",
        b"LANDING PAGES",
        b"TOAST + META ANALYSIS",
    ):
        assert area in response.data


def test_idea_endpoint_returns_ideas_without_generating_copy(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_campaign_ideas",
        lambda _brief: {
            "summary": "Test strategy summary",
            "ideas": [make_idea(f"Idea {index}") for index in range(1, 6)],
            "source": "OpenAI",
        },
    )

    response = main.app.test_client().post("/api/generate", json=BRIEF)
    data = response.get_json()

    assert response.status_code == 200
    assert data["summary"] == "Test strategy summary"
    assert len(data["ideas"]) == 5
    assert data["ideas"][0]["title"] == "Idea 1"
    assert data["ideas_source"] == "OpenAI"
    assert data["recommended_idea_index"] == 0
    assert "useful" in data["recommendation_reason"]
    assert "copy" not in data
    assert data["static_creatives"]
    assert data["landing_page"]["hero"]
    assert data["ads"]["rows"]


def test_idea_recommendation_matches_campaign_objective():
    ideas = generate_local_ideas(BRIEF)

    sales_index, sales_reason = recommend_campaign_idea(ideas, "Increase purchases")
    traffic_index, traffic_reason = recommend_campaign_idea(ideas, "Drive website traffic")
    awareness_index, awareness_reason = recommend_campaign_idea(ideas, "Build brand awareness")
    lead_index, lead_reason = recommend_campaign_idea(ideas, "Generate qualified leads")
    mixed_index, mixed_reason = recommend_campaign_idea(ideas, "Drive clicks and purchases")

    assert ideas[sales_index]["title"] == "The offer, without the fine-print surprise"
    assert "purchase-focused" in sales_reason
    assert ideas[traffic_index]["title"] == "The friction-to-relief story"
    assert "traffic test" in traffic_reason
    assert ideas[awareness_index]["title"] == "One product, several use cases"
    assert "awareness-test" in awareness_reason
    assert ideas[lead_index]["title"] in {
        "Proof through the product",
        "The question worth answering",
    }
    assert "qualified interest" in lead_reason
    assert ideas[mixed_index]["title"] == "The offer, without the fine-print surprise"
    assert "purchase-focused" in mixed_reason


def test_copy_endpoint_uses_the_user_selected_idea(monkeypatch):
    calls = []

    def fake_generate_copy(brief, idea):
        calls.append((brief, idea))
        return {
            "copy": {
                "hooks": ["Hook one", "Hook two"],
                "headlines": ["Headline one"],
                "primary_text": ["Text one"],
                "cta": ["Shop now"],
            },
            "source": "OpenAI",
        }

    monkeypatch.setattr(main, "generate_ad_copy", fake_generate_copy)
    selected_idea = make_idea("A quick dinner concept")

    response = main.app.test_client().post(
        "/api/generate-copy",
        json={"brief": BRIEF, "idea": selected_idea},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert calls == [(BRIEF, selected_idea)]
    assert data["idea"] == selected_idea
    assert data["copy_source"] == "OpenAI"
    assert data["copy"]["hooks"] == ["Hook one", "Hook two"]


def test_copy_endpoint_rejects_missing_idea():
    response = main.app.test_client().post("/api/generate-copy", json={"brief": BRIEF})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Select one campaign concept before continuing."


def test_image_prompt_endpoint_builds_prompt_from_brief_direction_and_idea():
    selected_idea = make_idea("Product demonstration concept")
    response = main.app.test_client().post(
        "/api/generate-image-prompt",
        json={
            "brief": BRIEF,
            "creative_direction": "Show the product in a warm, natural kitchen.",
            "aspect_ratio": "1:1",
            "idea": selected_idea,
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "Campaign prompt builder"
    assert data["aspect_ratio"] == "1:1"
    assert "Example Brand" in data["prompt"]
    assert "young families" in data["prompt"]
    assert "Show the product in a warm, natural kitchen." in data["prompt"]
    assert "Product demonstration concept" in data["prompt"]
    assert "One clear takeaway for the audience." in data["prompt"]
    assert "Do not render text, letters, logos, watermarks" in data["prompt"]


def test_image_prompt_endpoint_works_without_selected_idea():
    response = main.app.test_client().post(
        "/api/generate-image-prompt",
        json={
            "brief": BRIEF,
            "creative_direction": "A clean product hero.",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["aspect_ratio"] == "4:5"
    assert "No campaign concept is selected" in response.get_json()["prompt"]


def test_image_prompt_endpoint_rejects_unsupported_aspect_ratio():
    response = main.app.test_client().post(
        "/api/generate-image-prompt",
        json={
            "brief": BRIEF,
            "creative_direction": "A clean product hero.",
            "aspect_ratio": "3:2",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Choose an aspect ratio of 4:5, 1:1, or 9:16."


def test_idea_endpoint_rejects_missing_brief_fields():
    response = main.app.test_client().post("/api/generate", json={"brand": "Example Brand"})

    assert response.status_code == 400
    assert "Please fill in" in response.get_json()["error"]


def test_campaign_generation_reports_openai_failure(monkeypatch):
    def fail_generation(_brief):
        raise RuntimeError("OpenAI request failed")

    monkeypatch.setattr(main, "generate_campaign_ideas", fail_generation)

    response = main.app.test_client().post("/api/generate", json=BRIEF)

    assert response.status_code == 502
    assert response.get_json()["error"] == "OpenAI request failed"


def test_idea_generation_uses_labeled_local_templates_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    output = llm_service.generate_campaign_ideas(BRIEF)

    assert output["source"] == "Local templates (no OpenAI key configured)"
    assert "Example Brand" in output["summary"]
    assert len(output["ideas"]) == 5
    assert all(set(IDEA_FIELDS) <= idea.keys() for idea in output["ideas"])
    assert len({idea["title"] for idea in output["ideas"]}) == 5
    assert len({idea["strategic_angle"] for idea in output["ideas"]}) == 5
    assert all(
        idea["primary_kpi"] == "Purchase conversion rate, CPA and ROAS; CTR as a creative diagnostic"
        for idea in output["ideas"]
    )


def test_local_idea_kpis_follow_campaign_goal(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    lead_brief = {**BRIEF, "goal": "Generate qualified leads"}
    traffic_brief = {**BRIEF, "goal": "Increase website traffic and clicks"}
    mixed_brief = {**BRIEF, "goal": "Drive clicks and purchases"}

    lead_ideas = llm_service.generate_campaign_ideas(lead_brief)["ideas"]
    traffic_ideas = llm_service.generate_campaign_ideas(traffic_brief)["ideas"]
    mixed_ideas = llm_service.generate_campaign_ideas(mixed_brief)["ideas"]

    assert all(idea["primary_kpi"] == "Qualified lead rate and cost per qualified lead" for idea in lead_ideas)
    assert all(idea["primary_kpi"] == "Outbound CTR and CPC" for idea in traffic_ideas)
    assert all("ROAS" in idea["primary_kpi"] for idea in mixed_ideas)


def test_copy_generation_local_fallback_uses_selected_idea(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    selected_idea = make_idea("Highlight easy weeknight dinners")

    output = llm_service.generate_ad_copy(BRIEF, selected_idea)

    assert output["source"] == "Local templates (no OpenAI key configured)"
    assert all(selected_idea["strategic_angle"] in hook for hook in output["copy"]["hooks"])
    assert all(
        claim not in text.lower()
        for field in ("hooks", "headlines", "primary_text")
        for text in output["copy"][field]
        for claim in ("guaranteed results", "delivers them", "faster results", "see the difference")
    )


def test_invalid_openai_key_uses_demo_fallback_for_campaign_and_copy(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "invalid-test-key")

    def fail_request(*_args, **_kwargs):
        raise RuntimeError("Authentication failed")

    monkeypatch.setattr(llm_service, "_request_json", fail_request)
    idea_output = llm_service.generate_campaign_ideas(BRIEF)
    selected_idea = idea_output["ideas"][0]
    copy_output = llm_service.generate_ad_copy(BRIEF, selected_idea)

    assert idea_output["source"] == llm_service.AI_FALLBACK_SOURCE
    assert len(idea_output["ideas"]) == 5
    assert copy_output["source"] == llm_service.AI_FALLBACK_SOURCE
    assert len(copy_output["copy"]["hooks"]) == 3
    assert all(selected_idea["strategic_angle"] in hook for hook in copy_output["copy"]["hooks"])


def test_openai_video_and_edit_failures_use_demo_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "invalid-test-key")

    def fail_request(*_args, **_kwargs):
        raise RuntimeError("Authentication failed")

    monkeypatch.setattr(llm_service, "_request_json", fail_request)
    video = llm_service.generate_timed_video_script(BRIEF, 15)
    edit = llm_service.generate_video_edit_plan(
        [{
            "start_seconds": 0,
            "end_seconds": 5,
            "beat": "Open",
            "visual": "Scene",
            "voiceover": "A short line.",
            "on_screen_text": "",
        }],
        3,
    )

    assert video["source"] == llm_service.AI_FALLBACK_SOURCE
    assert video["script"][-1]["end_seconds"] == 15
    assert edit["source"] == llm_service.AI_FALLBACK_SOURCE
    assert edit["clips"][0]["start_seconds"] == 0


def test_idea_generation_uses_structured_openai_request(monkeypatch):
    sample = {
        "summary": "A test strategy",
        "ideas": [make_idea(f"Distinct campaign concept {index}") for index in range(1, 6)],
    }
    calls = []

    class FakeOpenAI:
        def __init__(self, api_key):
            assert api_key == "test-key"

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    calls.append(kwargs)
                    message = SimpleNamespace(content=json.dumps(sample))
                    return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service, "OpenAI", FakeOpenAI)

    output = llm_service.generate_campaign_ideas(BRIEF)

    assert output["source"] == "OpenAI"
    assert len(output["ideas"]) == 5
    assert len(calls) == 1
    assert calls[0]["response_format"]["type"] == "json_schema"
    idea_schema = calls[0]["response_format"]["json_schema"]["schema"]["properties"]["ideas"]["items"]
    assert set(IDEA_FIELDS) == set(idea_schema["required"])
    prompt = calls[0]["messages"][1]["content"]
    assert "control-versus-variant" in prompt
    assert "meaningfully different" in prompt


def test_copy_generation_openai_prompt_contains_selected_idea(monkeypatch):
    selected_idea = make_idea("Spotlight simple dinners")
    sample = {
        "hooks": ["Hook one", "Hook two", "Hook three"],
        "headlines": ["Headline one", "Headline two", "Headline three"],
        "primary_text": ["Text one", "Text two", "Text three"],
        "cta": "Shop now",
    }
    calls = []

    class FakeOpenAI:
        def __init__(self, api_key):
            assert api_key == "test-key"

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    calls.append(kwargs)
                    message = SimpleNamespace(content=json.dumps(sample))
                    return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service, "OpenAI", FakeOpenAI)

    output = llm_service.generate_ad_copy(BRIEF, selected_idea)

    assert output["source"] == "OpenAI"
    assert len(output["copy"]["hooks"]) == 3
    assert json.dumps(selected_idea) in calls[0]["messages"][1]["content"]


def test_video_endpoint_generates_requested_duration_concept_and_runtime_instructions(monkeypatch):
    calls = []

    def fake_generate_video(brief, duration_seconds, idea, instructions):
        calls.append((brief, duration_seconds, idea, instructions))
        return {
            "script": [{
                "start_seconds": 0,
                "end_seconds": duration_seconds,
                "beat": "Complete story",
                "visual": "Show the product",
                "voiceover": "A concise line.",
                "on_screen_text": "Shop now",
            }],
            "duration_seconds": duration_seconds,
            "source": "OpenAI",
        }

    monkeypatch.setattr(main, "generate_timed_video_script", fake_generate_video)
    selected_idea = make_idea("Selected campaign concept")
    response = main.app.test_client().post(
        "/api/generate-video",
        json={
            "brief": BRIEF,
            "duration_seconds": 45,
            "idea": selected_idea,
            "instructions": "Show the product earlier.",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert calls == [(BRIEF, 45, selected_idea, "Show the product earlier.")]
    assert data["duration_seconds"] == 45
    assert data["script_source"] == "OpenAI"


def test_video_endpoint_rejects_unsupported_duration():
    response = main.app.test_client().post(
        "/api/generate-video",
        json={"brief": BRIEF, "duration_seconds": 20},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Choose a video duration of 15, 30, 45, or 60 seconds."


def test_video_endpoint_rejects_oversized_runtime_instructions():
    response = main.app.test_client().post(
        "/api/generate-video",
        json={"brief": BRIEF, "duration_seconds": 30, "instructions": "x" * 1001},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "'instructions' must be 1000 characters or fewer."


def test_local_video_revision_attaches_runtime_direction(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    output = llm_service.generate_timed_video_script(
        BRIEF, 15, None, "Use shorter voiceover lines."
    )

    assert output["source"] == "Local template (revision note attached)"
    assert "Revision direction for human editing: Use shorter voiceover lines." in output["script"][0]["visual"]


def test_ugc_prompt_endpoint_uses_selected_idea_and_safety_guidance():
    selected_idea = make_idea("Product demonstration")
    response = main.app.test_client().post(
        "/api/generate-ugc-prompt",
        json={
            "brief": BRIEF,
            "format": "creator_demo",
            "aspect_ratio": "9:16",
            "idea": selected_idea,
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "UGC prompt builder"
    assert data["aspect_ratio"] == "9:16"
    assert "Product demonstration" in data["prompt"]
    assert "not a fabricated customer testimonial" in data["prompt"]
    assert "does not generate video" in data["prompt"]


def test_edit_timeline_splits_scenes_and_preserves_continuity(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    scenes = [
        {
            "start_seconds": 0,
            "end_seconds": 8,
            "beat": "Product demo",
            "visual": "Show the real product",
            "voiceover": "A verified line.",
            "on_screen_text": "Shop now",
        },
        {
            "start_seconds": 8,
            "end_seconds": 12,
            "beat": "CTA",
            "visual": "Close on product",
            "voiceover": "Take a look.",
            "on_screen_text": "",
        },
    ]
    response = main.app.test_client().post(
        "/api/build-edit-timeline",
        json={
            "script": scenes,
            "split_interval_seconds": 4,
            "instructions": "Keep the pace natural.",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["clip_count"] == 3
    assert data["duration_seconds"] == 12
    assert data["clips"][0]["start_seconds"] == 0
    assert data["clips"][-1]["end_seconds"] == 12
    assert all(
        data["clips"][index]["end_seconds"] == data["clips"][index + 1]["start_seconds"]
        for index in range(len(data["clips"]) - 1)
    )
    assert data["clips"][1]["voiceover"] == ""
    assert data["clips"][0]["editor_note"] == "Keep the pace natural."


def make_video_frames(duration_seconds=5.0):
    return [
        {
            "timestamp_seconds": timestamp,
            "image": "data:image/jpeg;base64,/9j/2Q==",
        }
        for timestamp in (duration_seconds * 0.1, duration_seconds * 0.5, duration_seconds * 0.9)
    ]


def test_video_edit_analysis_requires_three_valid_frames():
    response = main.app.test_client().post(
        "/api/analyze-edit-video",
        json={"duration_seconds": 5, "frames": []},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Extract exactly three frames from the uploaded video."


def test_video_edit_analysis_rejects_invalid_duration_and_frame_data():
    client = main.app.test_client()
    invalid_duration = client.post(
        "/api/analyze-edit-video",
        json={"duration_seconds": 181, "frames": make_video_frames()},
    )
    invalid_frame = client.post(
        "/api/analyze-edit-video",
        json={
            "duration_seconds": 5,
            "frames": [
                {"timestamp_seconds": timestamp, "image": "data:image/png;base64,AAAA"}
                for timestamp in (0.5, 2.5, 4.5)
            ],
        },
    )

    assert invalid_duration.status_code == 400
    assert invalid_frame.status_code == 400
    assert invalid_frame.get_json()["error"] == "Send the three extracted frames as JPEG images."


def test_video_edit_analysis_local_fallback_covers_video_duration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = main.app.test_client().post(
        "/api/analyze-edit-video",
        json={
            "duration_seconds": 5.25,
            "frames": make_video_frames(5.25),
            "split_interval_seconds": 3,
            "instructions": "Keep the cut clean.",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "Local demo (no OpenAI key configured)"
    assert data["duration_seconds"] == 5.25
    assert data["clip_count"] == 2
    assert data["clips"][0]["start_seconds"] == 0
    assert data["clips"][-1]["end_seconds"] == 5.25
    assert "were not analyzed" in data["analysis_summary"]
    assert data["edit_suggestions"] == []


def test_video_edit_analysis_sends_only_three_frames_to_openai(monkeypatch):
    duration = 5.125
    calls = []
    sample = {
        "analysis_summary": "A product is visible in the opening and closing samples.",
        "edit_suggestions": [
            {"focus": "Opening", "suggestion": "Start on the clearest product frame."},
            {"focus": "Pacing", "suggestion": "Hold longer on the central product view."},
            {"focus": "Ending", "suggestion": "End on the visible product and verify the source."},
        ],
        "clips": [{
            "start_seconds": 0,
            "end_seconds": duration,
            "beat": "Product close",
            "visual": "Hold on the product visible in the sampled frames.",
            "voiceover": "",
            "on_screen_text": "Explore more",
            "cut_note": "End on the clear product frame.",
        }],
    }

    class FakeOpenAI:
        def __init__(self, api_key):
            assert api_key == "test-key"

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    calls.append(kwargs)
                    message = SimpleNamespace(content=json.dumps(sample))
                    return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service, "OpenAI", FakeOpenAI)
    frames = make_video_frames(duration)
    response = main.app.test_client().post(
        "/api/analyze-edit-video",
        json={
            "duration_seconds": duration,
            "frames": frames,
            "split_interval_seconds": 6,
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "OpenAI visual analysis"
    assert data["analysis_summary"] == sample["analysis_summary"]
    assert data["edit_suggestions"] == sample["edit_suggestions"]
    assert data["clips"][-1]["end_seconds"] == duration
    content = calls[0]["messages"][1]["content"]
    image_parts = [part for part in content if part["type"] == "image_url"]
    assert len(image_parts) == 3
    assert [part["image_url"]["url"] for part in image_parts] == [
        frame["image"] for frame in frames
    ]
    assert all(part["image_url"]["detail"] == "high" for part in image_parts)
    assert "5.125 seconds" in content[0]["text"]
    assert "Never describe something as moving" in content[0]["text"]


def test_media_plan_is_brief_based_not_ads_report_and_budget_sums():
    response = main.app.test_client().post(
        "/api/media-plan",
        json={"brief": BRIEF, "daily_budget": 100, "idea": make_idea("Demo angle")},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "Rule-based planning assistant"
    assert data["concept"] == "Demo angle"
    assert sum(item["daily_budget"] for item in data["allocations"]) == 100
    assert data["primary_kpi"]
    assert any("no ad account" in item.lower() for item in data["guardrails"])


def test_media_plan_rejects_out_of_range_budget():
    response = main.app.test_client().post(
        "/api/media-plan",
        json={"brief": BRIEF, "daily_budget": 0},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Enter a daily budget between $1 and $100,000."


def test_local_video_script_matches_each_supported_duration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    selected_idea = make_idea("Selected video concept")

    for duration in (15, 30, 45, 60):
        output = llm_service.generate_timed_video_script(BRIEF, duration, selected_idea)
        scenes = output["script"]
        assert output["duration_seconds"] == duration
        assert output["source"] == "Local template"
        assert scenes[0]["start_seconds"] == 0
        assert scenes[-1]["end_seconds"] == duration
        assert all(
            scenes[index]["end_seconds"] == scenes[index + 1]["start_seconds"]
            for index in range(len(scenes) - 1)
        )
        assert all("Write one concise" not in scene["voiceover"] for scene in scenes)
        assert any(scene["visual"] == selected_idea["creative_execution"] for scene in scenes)


def test_landing_page_export_downloads_standalone_html():
    response = main.app.test_client().post(
        "/api/export-landing-page",
        json={
            "brief": BRIEF,
            "cta_url": "https://example.com/signup",
            "ad_copy": {
                "headline": "A faster weeknight plan",
                "body": "See how the meal kit fits your routine.",
                "cta": "Shop now",
            },
        },
    )

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "attachment;" in response.headers["Content-Disposition"]
    assert "example-brand-landing-page.html" in response.headers["Content-Disposition"]
    html = response.get_data(as_text=True)
    assert "<!doctype html>" in html
    assert "<style>" in html
    assert "https://example.com/signup" in html
    assert "A faster weeknight plan" in html
    assert "See how the meal kit fits your routine." in html
    assert "Example Brand" in html
    assert "meal kits" in html
    assert "20% off" in html
    assert "product-stage" in html
    assert "THE MESSAGE FROM YOUR AD" in html
    assert "@media (max-width: 520px)" in html
    assert "https://fonts.googleapis.com" not in html
    assert "<script" not in html
    assert "#d8ed65" in html
    assert "#3567c8" in html
    assert "✳" not in html


def test_landing_page_export_escapes_content_and_uses_safe_cta_default():
    brief = {
        **BRIEF,
        "brand": "<script>alert(1)</script>",
        "product": "<img src=x onerror=alert(1)>",
        "offer": "<script>alert('offer')</script>",
    }
    response = main.app.test_client().post(
        "/api/export-landing-page",
        json={"brief": brief},
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;script&gt;alert(&#x27;offer&#x27;)&lt;/script&gt;" in html
    assert 'href="#get-started"' in html
    assert "replace this button destination" in html.lower()


def test_landing_page_export_rejects_non_web_cta_url():
    response = main.app.test_client().post(
        "/api/export-landing-page",
        json={"brief": BRIEF, "cta_url": "javascript:alert(1)"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "The CTA destination must be a valid HTTPS or HTTP URL."


def test_openai_video_script_is_timed_and_uses_selected_concept(monkeypatch):
    sample = {
        "scenes": [
            {"start_seconds": 0, "end_seconds": 5, "beat": "Hook", "visual": "Open", "voiceover": "Start.", "on_screen_text": ""},
            {"start_seconds": 5, "end_seconds": 10, "beat": "Demo", "visual": "Show product", "voiceover": "Explore.", "on_screen_text": ""},
            {"start_seconds": 10, "end_seconds": 15, "beat": "CTA", "visual": "Close", "voiceover": "Shop now.", "on_screen_text": "Shop now"},
        ],
    }
    calls = []

    class FakeOpenAI:
        def __init__(self, api_key):
            assert api_key == "test-key"

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    calls.append(kwargs)
                    message = SimpleNamespace(content=json.dumps(sample))
                    return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service, "OpenAI", FakeOpenAI)
    selected_idea = make_idea("Selected video concept")

    output = llm_service.generate_timed_video_script(BRIEF, 15, selected_idea)

    assert output["source"] == "OpenAI"
    assert output["script"] == sample["scenes"]
    assert calls[0]["response_format"]["type"] == "json_schema"
    assert json.dumps(selected_idea) in calls[0]["messages"][1]["content"]
