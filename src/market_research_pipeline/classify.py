from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from .models import ClassifiedPost, PostRecord


def load_taxonomy(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).lower()


def first_matching_label(text: str, mapping: dict[str, list[str]], default: str = "") -> str:
    text_norm = normalize_text(text)
    best_label = default
    best_hits = 0
    for label, keywords in mapping.items():
        hits = sum(1 for keyword in keywords if keyword.lower() in text_norm)
        if hits > best_hits:
            best_hits = hits
            best_label = label
    return best_label


def detect_tool(text: str, tools: Iterable[str]) -> str:
    text_norm = normalize_text(text)
    for tool in tools:
        if tool.lower() in text_norm:
            return tool
    return ""


def extract_quote(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    scored = sorted(
        sentences,
        key=lambda sentence: (
            int(any(token in sentence.lower() for token in ["need", "want", "hate", "privacy", "trust", "context", "workflow"])),
            len(sentence),
        ),
        reverse=True,
    )
    for sentence in scored:
        sentence = sentence.strip()
        if 24 <= len(sentence) <= 220:
            return sentence
    return text.strip()[:220]


def infer_sentiment(text: str) -> str:
    text_norm = normalize_text(text)
    negative = ["hate", "friction", "lying", "wrong", "pain", "problem", "overhead", "drowning"]
    positive = ["helpful", "useful", "love", "great", "core tool", "just works"]
    neg_hits = sum(1 for word in negative if word in text_norm)
    pos_hits = sum(1 for word in positive if word in text_norm)
    if neg_hits > pos_hits:
        return "negative"
    if pos_hits > neg_hits:
        return "positive"
    return "mixed" if neg_hits and pos_hits else "neutral"


def infer_buying_signal(text: str, mapping: dict[str, list[str]]) -> str:
    text_norm = normalize_text(text)
    for label in ["strong", "medium", "weak"]:
        keywords = mapping.get(label, [])
        if any(keyword in text_norm for keyword in keywords):
            return label
    return "weak"


def score_pain(text: str) -> int:
    text_norm = normalize_text(text)
    strong = ["hate", "drowning", "insanely", "core tool", "private", "trust", "gdpr", "context amnesia"]
    medium = ["friction", "pain", "workflow", "setup", "problem", "not useful"]
    score = 1
    if any(token in text_norm for token in medium):
        score = 3
    if any(token in text_norm for token in strong):
        score = 4
    if sum(token in text_norm for token in strong) >= 2:
        score = 5
    return score


def score_wtp(buying_signal: str, segment: str) -> int:
    base = {"weak": 1, "medium": 3, "strong": 5}.get(buying_signal, 1)
    if segment == "small_team_operators" and base < 5:
        base += 1
    return min(base, 5)


def score_fit(segment: str, pain_point: str, trust_concern: str, desire: str) -> int:
    score = 2
    if segment in {"second_brain_power_users", "small_team_operators", "creators"}:
        score += 1
    if pain_point in {"context fragmentation and amnesia", "trust and privacy risk", "setup and configuration overhead"}:
        score += 1
    if trust_concern or desire in {"source-grounded synthesis", "local-first or privacy-preserving AI", "workflow-specific copilots"}:
        score += 1
    return min(score, 5)


def feature_implication(post: ClassifiedPost) -> str:
    if post.trust_concern:
        return "Prioritize source links, reviewable memory updates, and explicit privacy/provenance controls."
    if post.pain_point == "context fragmentation and amnesia":
        return "Emphasize continuity features like Today, what changed, and project-aware context carryover."
    if post.segment == "creators":
        return "Package the workflow as a creator/artist copilot with release planning and continuity, not generic PKM."
    if post.segment == "small_team_operators":
        return "Lead with team briefs, follow-up tracking, and shared context summaries."
    return "Keep the first workflow narrow, inspectable, and tied to a concrete before/after outcome."


def messaging_implication(post: ClassifiedPost) -> str:
    if post.trust_concern:
        return "Message the product as reviewable, source-aware, and under user control."
    if post.pain_point == "setup and configuration overhead":
        return "Avoid 'build your second brain' language; promise fast utility from a small source set."
    if post.pain_point == "hallucinations and weak grounding":
        return "Lead with evidence-backed answers and explain-this-answer framing."
    return "Anchor messaging in concrete workflow outcomes instead of broad AI assistant claims."


def switching_trigger(post: ClassifiedPost) -> str:
    if post.pain_point == "context fragmentation and amnesia":
        return "Repeated re-explaining and scattered context create switching pressure."
    if post.trust_concern:
        return "Users switch when a tool proves privacy-respecting and source-reviewable."
    if post.pain_point == "setup and configuration overhead":
        return "Users will move if onboarding becomes clipping-first and low-friction."
    return "A visible, job-specific improvement over existing note/AI workflows."


def classify_post(post: PostRecord, taxonomy: dict) -> ClassifiedPost:
    text = " ".join(part for part in [post.title, post.body, post.raw_text] if part).strip()
    segment = first_matching_label(text, taxonomy["segments"], default="second_brain_power_users")
    pain_point = first_matching_label(text, taxonomy["pain_points"])
    desire = first_matching_label(text, taxonomy["desires"])
    objection = first_matching_label(text, taxonomy["objections"])
    trust_concern = first_matching_label(text, taxonomy["trust_concerns"])
    job = first_matching_label(text, taxonomy["jobs"], default="organize scattered information into a usable context layer")
    buying_signal = infer_buying_signal(text, taxonomy["buying_signals"])
    current_tool = detect_tool(text, taxonomy["tools"])
    sentiment = infer_sentiment(text)

    classified = ClassifiedPost(
        **post.to_dict(),
        job_to_be_done=job,
        pain_point=pain_point,
        desire=desire,
        objection=objection,
        trust_concern=trust_concern,
        current_tool=current_tool,
        segment=segment,
        buying_signal=buying_signal,
        sentiment=sentiment,
        useful_quote=extract_quote(post.raw_text or text),
    )
    classified.pain_intensity = score_pain(text)
    classified.willingness_to_pay_score = score_wtp(classified.buying_signal, classified.segment)
    classified.fit_score = score_fit(classified.segment, classified.pain_point, classified.trust_concern, classified.desire)
    classified.feature_implication = feature_implication(classified)
    classified.messaging_implication = messaging_implication(classified)
    classified.switching_trigger = switching_trigger(classified)
    return classified

