"""Simple ad performance analytics for the mock dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_ad_data(file_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(file_path)


def summarize_ads(df: pd.DataFrame) -> Dict[str, float]:
    summary = {
        "total_spend": float(df["spend"].sum()),
        "total_clicks": float(df["clicks"].sum()),
        "total_conversions": float(df["conversions"].sum()),
        "avg_ctr": float(df["ctr"].mean() * 100),
        "avg_cpc": float(df["cpc"].mean()),
        "avg_roas": float(df["roas"].mean()),
    }
    return summary


def recommend_actions(df: pd.DataFrame) -> List[str]:
    top_campaign = df.loc[df["roas"].idxmax(), "campaign"]
    top_hook = df.loc[df["ctr"].idxmax(), "hook"]
    highest_cost = df.loc[df["cpc"].idxmax(), "campaign"]

    return [
        f"Shift additional budget toward the '{top_campaign}' campaign because it has the strongest ROAS.",
        f"Use the '{top_hook}' hook structure more often in top-of-funnel creative testing.",
        f"Reduce spend on the '{highest_cost}' campaign if CPC is too high and creative is not improving quickly.",
        "Keep a short human review loop for angle changes before broad rollout.",
    ]
