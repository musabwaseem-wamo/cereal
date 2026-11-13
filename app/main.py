from __future__ import annotations

import base64
import binascii
import math
from io import BytesIO
from pathlib import Path
import re
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file
from openai import OpenAIError

from .modules.analytics import load_ad_data, recommend_actions, summarize_ads
from .modules.idea_recommendation import recommend_campaign_idea
from .modules.generators import (
    generate_landing_page,
    generate_review_checklist,
    generate_static_creative_concepts,
    generate_video_script,
)
from .modules.media_buyer import build_media_plan
from .modules.image_prompt import SUPPORTED_ASPECT_RATIOS, build_image_prompt
from .modules.landing_export import build_standalone_landing_page, landing_page_filename
from .modules.ugc_prompt import build_ugc_prompt
from .modules.llm_service import (
    CAMPAIGN_IDEA_FIELDS,
    generate_ad_copy,
    generate_campaign_ideas,
    generate_timed_video_script,
    generate_video_edit_plan,
    generate_video_edit_plan_from_video,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "mock_ads.csv"
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024
MAX_EDIT_VIDEO_DURATION_SECONDS = 180
MAX_EDIT_FRAME_BYTES = 500 * 1024


def build_campaign_output(brief: dict[str, str]) -> dict[str, Any]:
    ads = load_ad_data(DATA_PATH)
    campaign_content = generate_campaign_ideas(brief)
    recommended_idea_index, recommendation_reason = recommend_campaign_idea(
        campaign_content["ideas"],
        brief["goal"],
    )
    return {
        "brief": brief,
        "summary": campaign_content["summary"],
        "summary_source": campaign_content["source"],
        "ideas": campaign_content["ideas"],
        "ideas_source": campaign_content["source"],
        "recommended_idea_index": recommended_idea_index,
        "recommendation_reason": recommendation_reason,
        "static_creatives": generate_static_creative_concepts(brief),
        "video": {"ugc_ideas": generate_video_script(brief)["ugc_ideas"]},
        "landing_page": generate_landing_page(brief),
        "review_checklist": generate_review_checklist(brief),
        "ads": {
            "summary": summarize_ads(ads),
            "rows": ads.to_dict(orient="records"),
            "recommendations": recommend_actions(ads),
        },
    }


def parse_brief(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("Send the campaign brief as a JSON object.")

    fields = ("brand", "product", "audience", "offer", "goal", "channel", "cta", "tone", "constraints")
    brief: dict[str, str] = {}
    for field in fields:
        value = payload.get(field, "")
        if not isinstance(value, str):
            raise ValueError(f"'{field}' must be text.")
        brief[field] = value.strip()

    missing = [field for field in fields[:7] if not brief[field]]
    if missing:
        raise ValueError(f"Please fill in: {', '.join(missing)}.")
    return brief


def parse_selected_idea(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("Select one campaign concept before continuing.")
    idea: dict[str, str] = {}
    for field in CAMPAIGN_IDEA_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("The selected campaign concept is incomplete.")
        if len(value) > 2000:
            raise ValueError("The selected campaign concept is too long.")
        idea[field] = value.strip()
    return idea


def parse_video_duration(payload: object) -> int:
    if not isinstance(payload, int) or isinstance(payload, bool) or payload not in {15, 30, 45, 60}:
        raise ValueError("Choose a video duration of 15, 30, 45, or 60 seconds.")
    return payload


def parse_runtime_instructions(payload: object, field: str = "instructions") -> str:
    if payload is None:
        return ""
    if not isinstance(payload, str):
        raise ValueError(f"'{field}' must be text.")
    if len(payload) > 1000:
        raise ValueError(f"'{field}' must be 1000 characters or fewer.")
    return payload.strip()


def parse_edit_video_duration(payload: object) -> float:
    if not isinstance(payload, (int, float)) or isinstance(payload, bool):
        raise ValueError("Choose a video at least 0.5 seconds and no longer than 3 minutes.")
    try:
        duration_seconds = float(payload)
    except OverflowError as error:
        raise ValueError("Choose a video at least 0.5 seconds and no longer than 3 minutes.") from error
    if (
        not math.isfinite(duration_seconds)
        or not 0.5 <= duration_seconds <= MAX_EDIT_VIDEO_DURATION_SECONDS
    ):
        raise ValueError("Choose a video at least 0.5 seconds and no longer than 3 minutes.")
    return round(duration_seconds, 3)


def parse_edit_video_frames(payload: object, duration_seconds: float) -> list[dict[str, object]]:
    if not isinstance(payload, list) or len(payload) != 3:
        raise ValueError("Extract exactly three frames from the uploaded video.")

    frames: list[dict[str, object]] = []
    previous_timestamp = -1.0
    for frame in payload:
        if not isinstance(frame, dict):
            raise ValueError("Each extracted video frame must include its timestamp and image.")
        timestamp = frame.get("timestamp_seconds")
        image_data = frame.get("image")
        try:
            numeric_timestamp = float(timestamp)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("Video frame timestamps must be ordered and within the uploaded video.") from error
        if (
            not isinstance(timestamp, (int, float))
            or isinstance(timestamp, bool)
            or not math.isfinite(numeric_timestamp)
            or not previous_timestamp < numeric_timestamp < duration_seconds
        ):
            raise ValueError("Video frame timestamps must be ordered and within the uploaded video.")
        if not isinstance(image_data, str) or not image_data.startswith("data:image/jpeg;base64,"):
            raise ValueError("Send the three extracted frames as JPEG images.")
        encoded_image = image_data.removeprefix("data:image/jpeg;base64,")
        if len(encoded_image) > 4 * math.ceil(MAX_EDIT_FRAME_BYTES / 3):
            raise ValueError("Each extracted frame must be 500 KB or smaller.")
        try:
            image_bytes = base64.b64decode(encoded_image, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("An extracted video frame is not valid base64 image data.") from error
        if len(image_bytes) > MAX_EDIT_FRAME_BYTES or not image_bytes.startswith(b"\xff\xd8\xff"):
            raise ValueError("Each extracted frame must be a JPEG image no larger than 500 KB.")
        frames.append({"timestamp_seconds": round(numeric_timestamp, 3), "image": image_data})
        previous_timestamp = numeric_timestamp
    return frames


def parse_script_scenes(payload: object) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not 1 <= len(payload) <= 20:
        raise ValueError("Provide between one and twenty timed script scenes.")
    scenes: list[dict[str, Any]] = []
    expected_start = 0
    for scene in payload:
        if not isinstance(scene, dict):
            raise ValueError("Each script scene must be an object.")
        start = scene.get("start_seconds")
        end = scene.get("end_seconds")
        if (
            not isinstance(start, int) or isinstance(start, bool)
            or not isinstance(end, int) or isinstance(end, bool)
            or start != expected_start or end <= start or end > 60
        ):
            raise ValueError("Script scenes must be continuous and fit within 60 seconds.")
        fields = ("beat", "visual", "voiceover", "on_screen_text")
        validated: dict[str, Any] = {"start_seconds": start, "end_seconds": end}
        for field in fields:
            value = scene.get(field, "")
            if not isinstance(value, str) or len(value) > 2000:
                raise ValueError("Each scene must contain valid text fields.")
            validated[field] = value.strip()
        scenes.append(validated)
        expected_start = end
    return scenes


def parse_image_aspect_ratio(payload: object) -> str:
    if not isinstance(payload, str) or payload not in SUPPORTED_ASPECT_RATIOS:
        raise ValueError("Choose an aspect ratio of 4:5, 1:1, or 9:16.")
    return payload


def generation_error(error: Exception):
    message = re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted API key]", str(error))
    app.logger.error("Campaign generation failed (%s): %s", type(error).__name__, message)
    return jsonify({"error": message}), 502


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/ads")
def ads_data():
    ads = load_ad_data(DATA_PATH)
    return jsonify({
        "summary": summarize_ads(ads),
        "rows": ads.to_dict(orient="records"),
        "recommendations": recommend_actions(ads),
    })


@app.post("/api/generate")
def generate():
    try:
        brief = parse_brief(request.get_json(silent=True))
        return jsonify(build_campaign_output(brief))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (OpenAIError, RuntimeError) as error:
        return generation_error(error)


@app.post("/api/generate-copy")
def generate_copy():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and selected idea as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        selected_idea = parse_selected_idea(payload.get("idea"))
        result = generate_ad_copy(brief, selected_idea)
        return jsonify({
            "idea": selected_idea,
            "copy": result["copy"],
            "copy_source": result["source"],
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (OpenAIError, RuntimeError) as error:
        return generation_error(error)


@app.post("/api/generate-video")
def generate_video():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and video duration as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        duration_seconds = parse_video_duration(payload.get("duration_seconds"))
        instructions = parse_runtime_instructions(payload.get("instructions"))
        idea_payload = payload.get("idea")
        selected_idea = parse_selected_idea(idea_payload) if idea_payload is not None else None
        result = generate_timed_video_script(brief, duration_seconds, selected_idea, instructions)
        return jsonify({
            "script": result["script"],
            "duration_seconds": result["duration_seconds"],
            "script_source": result["source"],
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (OpenAIError, RuntimeError) as error:
        return generation_error(error)


@app.post("/api/generate-ugc-prompt")
def generate_ugc_video_prompt():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and UGC format as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        format_key = payload.get("format")
        aspect_ratio = payload.get("aspect_ratio", "9:16")
        idea_payload = payload.get("idea")
        selected_idea = parse_selected_idea(idea_payload) if idea_payload is not None else None
        prompt = build_ugc_prompt(brief, format_key, aspect_ratio, selected_idea)
        return jsonify({"prompt": prompt, "source": "UGC prompt builder", "aspect_ratio": aspect_ratio})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/build-edit-timeline")
def build_edit_timeline():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the timed script as a JSON object.")
        scenes = parse_script_scenes(payload.get("script"))
        interval = payload.get("split_interval_seconds", 5)
        if not isinstance(interval, int) or isinstance(interval, bool) or interval not in {3, 4, 5, 6, 8, 10}:
            raise ValueError("Choose a clip split interval of 3, 4, 5, 6, 8, or 10 seconds.")
        instructions = parse_runtime_instructions(payload.get("instructions"), "editor instructions")
        result = generate_video_edit_plan(scenes, interval, instructions)
        return jsonify({
            "clips": result["clips"],
            "clip_count": len(result["clips"]),
            "duration_seconds": scenes[-1]["end_seconds"],
            "source": result["source"],
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (OpenAIError, RuntimeError) as error:
        return generation_error(error)


@app.post("/api/analyze-edit-video")
def analyze_edit_video():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the uploaded video's duration, three extracted frames, and editing notes.")
        duration_seconds = parse_edit_video_duration(payload.get("duration_seconds"))
        frames = parse_edit_video_frames(payload.get("frames"), duration_seconds)
        interval = payload.get("split_interval_seconds", 5)
        if not isinstance(interval, int) or isinstance(interval, bool) or interval not in {3, 4, 5, 6, 8, 10}:
            raise ValueError("Choose a clip split interval of 3, 4, 5, 6, 8, or 10 seconds.")
        instructions = parse_runtime_instructions(payload.get("instructions"), "editor instructions")
        script_payload = payload.get("script")
        scenes = parse_script_scenes(script_payload) if script_payload is not None else []
        result = generate_video_edit_plan_from_video(
            duration_seconds,
            frames,
            interval,
            instructions,
            scenes,
        )
        return jsonify({
            "clips": result["clips"],
            "clip_count": len(result["clips"]),
            "duration_seconds": duration_seconds,
            "analysis_summary": result["analysis_summary"],
            "edit_suggestions": result["edit_suggestions"],
            "source": result["source"],
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (OpenAIError, RuntimeError) as error:
        return generation_error(error)


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({"error": "The sampled frames are too large. Try a lower-resolution video."}), 413


@app.post("/api/media-plan")
def media_plan():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and daily budget as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        budget = payload.get("daily_budget")
        if not isinstance(budget, (int, float)) or isinstance(budget, bool) or not 1 <= budget <= 100000:
            raise ValueError("Enter a daily budget between $1 and $100,000.")
        idea_payload = payload.get("idea")
        selected_idea = parse_selected_idea(idea_payload) if idea_payload is not None else None
        return jsonify(build_media_plan(brief, float(budget), selected_idea))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/generate-image-prompt")
def generate_image_prompt():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and image direction as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        direction = payload.get("creative_direction")
        if not isinstance(direction, str):
            raise ValueError("Choose a static image direction first.")
        aspect_ratio = parse_image_aspect_ratio(payload.get("aspect_ratio", "4:5"))
        idea_payload = payload.get("idea")
        selected_idea = parse_selected_idea(idea_payload) if idea_payload is not None else None
        prompt = build_image_prompt(brief, direction, aspect_ratio, selected_idea)
        return jsonify({"prompt": prompt, "aspect_ratio": aspect_ratio, "source": "Campaign prompt builder"})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/export-landing-page")
def export_landing_page():
    payload = request.get_json(silent=True)
    try:
        if not isinstance(payload, dict):
            raise ValueError("Send the campaign brief and CTA destination as a JSON object.")
        brief = parse_brief(payload.get("brief"))
        landing_page = generate_landing_page(brief)
        html = build_standalone_landing_page(
            brand=brief["brand"],
            headline=landing_page["hero"],
            subhead=landing_page["subhead"],
            cta=landing_page["cta"],
            bullets=landing_page["bullets"],
            destination_url=payload.get("cta_url"),
            ad_copy=payload.get("ad_copy"),
            product=brief["product"],
            offer=brief["offer"],
        )
        return send_file(
            BytesIO(html.encode("utf-8")),
            mimetype="text/html",
            as_attachment=True,
            download_name=landing_page_filename(brief["brand"]),
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
