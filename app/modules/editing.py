"""Create a simple, editable cut timeline from a timed script."""

from __future__ import annotations

from typing import Any


def split_script_into_clips(
    scenes: list[dict[str, Any]],
    split_interval_seconds: int = 5,
    instructions: str = "",
) -> list[dict[str, Any]]:
    clips: list[dict[str, Any]] = []
    for scene in scenes:
        start = scene["start_seconds"]
        end = scene["end_seconds"]
        segment_start = start
        first_segment = True
        while segment_start < end:
            segment_end = min(segment_start + split_interval_seconds, end)
            clips.append({
                "start_seconds": segment_start,
                "end_seconds": segment_end,
                "beat": scene["beat"],
                "visual": scene["visual"],
                "voiceover": scene["voiceover"] if first_segment else "",
                "on_screen_text": scene["on_screen_text"] if first_segment else "",
                "cut_note": "Cut on action or a natural visual change." if segment_end < end else "Hold through the beat, then cut cleanly.",
                "editor_note": instructions.strip(),
            })
            segment_start = segment_end
            first_segment = False
    return clips
