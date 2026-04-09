from __future__ import annotations

import json
from pathlib import Path

from .storage import write_json, write_markdown


def discover_targets(targets_path: Path, concept_path: Path, output_json: Path, output_md: Path) -> dict:
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    concept = json.loads(concept_path.read_text(encoding="utf-8"))
    payload = {
        "focus_name": concept["focus_name"],
        "focus_description": concept["focus_description"],
        "screen_queries": concept["screen_queries"],
        "targets": targets,
    }
    write_json(output_json, payload)
    write_markdown(output_md, render_target_discovery_markdown(payload))
    return payload


def render_target_discovery_markdown(payload: dict) -> str:
    lines = [
        "# Source Discovery",
        "",
        f"Focus: **{payload['focus_name']}**",
        "",
        payload["focus_description"],
        "",
        "## Reddit Targets",
        "",
    ]
    for target in payload["targets"]["reddit"]:
        lines.append(f"- **{target['name']}** ({target['priority']}): {target['rationale']} {target['url']}")
    lines.extend(["", "## X Targets", ""])
    for target in payload["targets"]["x"]:
        lines.append(f"- **{target['name']}** (`@{target['handle']}` if profile; {target['priority']}): {target['rationale']} {target['url']}")
    if payload["targets"].get("forums"):
        lines.extend(["", "## Forum Targets", ""])
        for target in payload["targets"]["forums"]:
            lines.append(f"- **{target['name']}** ({target['priority']}): {target['rationale']} {target['url']}")
    lines.extend(["", "## Suggested Search Queries", ""])
    for platform, queries in payload["screen_queries"].items():
        lines.append(f"### {platform.title()}")
        lines.append("")
        for query in queries:
            lines.append(f"- `{query}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
