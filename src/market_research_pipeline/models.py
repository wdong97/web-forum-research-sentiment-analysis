from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PostRecord:
    post_id: str
    source: str
    source_type: str
    thread_id: str = ""
    url: str = ""
    created_at: str = ""
    author: str = ""
    author_handle: str = ""
    title: str = ""
    body: str = ""
    raw_text: str = ""
    lang: str = "en"
    score: float = 0.0
    comment_count: int = 0
    engagement: float = 0.0
    tags: list[str] = field(default_factory=list)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    ingest_run_id: str = ""
    ingested_at: str = ""
    snapshot_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ClassifiedPost(PostRecord):
    job_to_be_done: str = ""
    pain_point: str = ""
    desire: str = ""
    objection: str = ""
    trust_concern: str = ""
    current_tool: str = ""
    segment: str = ""
    buying_signal: str = ""
    sentiment: str = "neutral"
    useful_quote: str = ""
    feature_implication: str = ""
    messaging_implication: str = ""
    switching_trigger: str = ""
    pain_intensity: int = 1
    willingness_to_pay_score: int = 1
    fit_score: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

