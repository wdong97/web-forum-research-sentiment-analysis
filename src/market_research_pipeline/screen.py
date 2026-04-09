from __future__ import annotations

import json
from pathlib import Path

from .storage import read_jsonl, write_jsonl


def load_focus(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def _text(row: dict) -> str:
    return " ".join(str(row.get(key, "")) for key in ["title", "body", "text", "content", "raw_text", "parent_title", "parent_body"]).lower()


def concept_matches(row: dict, focus: dict) -> tuple[int, list[str]]:
    text = _text(row)
    hits: list[str] = []
    score = 0
    for concept, keywords in focus["concept_keywords"].items():
        matched = [keyword for keyword in keywords if keyword.lower() in text]
        if matched:
            hits.append(concept)
            score += min(len(matched), 3)
    if row.get("score"):
        score += 1
    if row.get("comment_count"):
        score += 1
    return score, hits


def screen_posts(input_path: Path, output_path: Path, focus_path: Path, min_score: int = 3) -> list[dict]:
    rows = read_jsonl(input_path)
    focus = load_focus(focus_path)
    screened: list[dict] = []
    for row in rows:
        score, hits = concept_matches(row, focus)
        if score < min_score:
            continue
        row = dict(row)
        row["screen_stage"] = "post"
        row["concept_relevance_score"] = score
        row["concept_hits"] = hits
        row["screen_reason"] = ", ".join(hits)
        screened.append(row)
    write_jsonl(output_path, screened)
    return screened


def screen_comments(input_path: Path, output_path: Path, focus_path: Path, min_score: int = 2) -> list[dict]:
    rows = read_jsonl(input_path)
    focus = load_focus(focus_path)
    screened: list[dict] = []
    for row in rows:
        score, hits = concept_matches(row, focus)
        if row.get("parent_title"):
            score += 1
        if score < min_score:
            continue
        row = dict(row)
        row["screen_stage"] = "comment"
        row["concept_relevance_score"] = score
        row["concept_hits"] = hits
        row["screen_reason"] = ", ".join(hits) or "context match"
        screened.append(row)
    write_jsonl(output_path, screened)
    return screened

