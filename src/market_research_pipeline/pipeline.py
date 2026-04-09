from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adapters import import_reddit_dir, import_reddit_thread, import_x_dir, import_x_export
from .classify import classify_post, load_taxonomy
from .cluster import cluster_posts
from .discovery import discover_targets
from .models import PostRecord
from .reports import (
    render_feature_signals,
    render_pricing_notes,
    render_research_summary,
    render_quotes,
    render_screening_summary,
    render_segment_analysis,
    render_weekly_market_report,
)
from .screen import screen_comments, screen_posts
from .storage import read_csv, read_jsonl, write_json, write_jsonl, write_markdown


def repo_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "source_discovery_json": repo_root / "data/discovery/source_targets.json",
        "source_discovery_md": repo_root / "reports/staging/source-discovery.md",
        "imported_reddit_posts": repo_root / "data/imports/reddit_posts.jsonl",
        "imported_reddit_comments": repo_root / "data/imports/reddit_comments.jsonl",
        "imported_x_posts": repo_root / "data/imports/x_posts.jsonl",
        "imported_x_comments": repo_root / "data/imports/x_comments.jsonl",
        "screened_posts": repo_root / "data/processed/screened_posts.jsonl",
        "screened_comments": repo_root / "data/processed/screened_comments.jsonl",
        "screened_posts_md": repo_root / "reports/staging/post-screening-summary.md",
        "screened_comments_md": repo_root / "reports/staging/comment-screening-summary.md",
        "merged_posts": repo_root / "data/imports/merged_posts.jsonl",
        "merged_comments": repo_root / "data/imports/merged_comments.jsonl",
        "classified_screened_posts": repo_root / "data/processed/classified_screened_posts.jsonl",
        "classified_screened_comments": repo_root / "data/processed/classified_screened_comments.jsonl",
        "theme_clusters_screened_posts": repo_root / "data/processed/theme_clusters_screened_posts.json",
        "theme_clusters_screened_comments": repo_root / "data/processed/theme_clusters_screened_comments.json",
        "research_summary": repo_root / "reports/staging/research-summary.md",
        "raw_posts": repo_root / "data/normalized/raw_posts.jsonl",
        "classified_posts": repo_root / "data/processed/classified_posts.jsonl",
        "theme_clusters": repo_root / "data/processed/theme_clusters.json",
        "weekly_market_report": repo_root / "reports/staging/weekly-market-report.md",
        "quotes": repo_root / "reports/staging/quotes.md",
        "feature_signals": repo_root / "reports/staging/feature-signals.md",
        "segment_analysis": repo_root / "reports/staging/segment-analysis.md",
        "pricing_notes": repo_root / "reports/staging/pricing-and-economics-notes.md",
    }


def run_target_discovery(repo_root: Path, targets_path: Path | None = None, focus_path: Path | None = None) -> dict:
    paths = repo_paths(repo_root)
    return discover_targets(
        targets_path or (repo_root / "configs/source_targets.json"),
        focus_path or (repo_root / "configs/concept_focus.json"),
        paths["source_discovery_json"],
        paths["source_discovery_md"],
    )


def run_post_screen(input_path: Path, repo_root: Path, min_score: int = 3, focus_path: Path | None = None) -> list[dict]:
    paths = repo_paths(repo_root)
    screened = screen_posts(input_path, paths["screened_posts"], focus_path or (repo_root / "configs/concept_focus.json"), min_score=min_score)
    write_markdown(paths["screened_posts_md"], render_screening_summary(screened, "post"))
    return screened


def run_comment_screen(input_path: Path, repo_root: Path, min_score: int = 2, focus_path: Path | None = None) -> list[dict]:
    paths = repo_paths(repo_root)
    screened = screen_comments(input_path, paths["screened_comments"], focus_path or (repo_root / "configs/concept_focus.json"), min_score=min_score)
    write_markdown(paths["screened_comments_md"], render_screening_summary(screened, "comment"))
    return screened


def run_reddit_import(input_path: Path, repo_root: Path) -> tuple[list[dict], list[dict]]:
    paths = repo_paths(repo_root)
    return import_reddit_thread(input_path, paths["imported_reddit_posts"], paths["imported_reddit_comments"])


def run_x_import(input_path: Path, repo_root: Path) -> tuple[list[dict], list[dict]]:
    paths = repo_paths(repo_root)
    return import_x_export(input_path, paths["imported_x_posts"], paths["imported_x_comments"])


def run_reddit_dir_import(input_dir: Path, repo_root: Path) -> tuple[list[dict], list[dict]]:
    paths = repo_paths(repo_root)
    return import_reddit_dir(input_dir, paths["imported_reddit_posts"], paths["imported_reddit_comments"])


def run_x_dir_import(input_dir: Path, repo_root: Path) -> tuple[list[dict], list[dict]]:
    paths = repo_paths(repo_root)
    return import_x_dir(input_dir, paths["imported_x_posts"], paths["imported_x_comments"])


def _merge_jsonl_files(input_paths: list[Path], output_path: Path) -> list[dict]:
    merged: list[dict] = []
    for path in input_paths:
        if path.exists():
            merged.extend(read_jsonl(path))
    write_jsonl(output_path, merged)
    return merged


def _ingest_row(row: dict[str, Any], source: str, snapshot_path: str) -> dict[str, Any]:
    explicit_raw_text = str(row.get("raw_text") or "").strip()
    combined_text = " ".join(str(row.get(key, "")) for key in ["title", "body", "text", "content", "raw_text"]).strip()
    created_at = row.get("created_at") or row.get("date") or ""
    score = float(row.get("score") or row.get("points") or 0)
    comment_count = int(row.get("comment_count") or row.get("num_comments") or 0)
    return PostRecord(
        post_id=str(row.get("post_id") or row.get("id") or uuid.uuid4()),
        source=source or str(row.get("source") or "unknown"),
        source_type=str(row.get("source_type") or "post"),
        thread_id=str(row.get("thread_id") or row.get("story_id") or ""),
        url=str(row.get("url") or ""),
        created_at=str(created_at),
        author=str(row.get("author") or ""),
        author_handle=str(row.get("author_handle") or ""),
        title=str(row.get("title") or ""),
        body=str(row.get("body") or row.get("text") or row.get("content") or ""),
        raw_text=explicit_raw_text or combined_text,
        score=score,
        comment_count=comment_count,
        engagement=float(row.get("engagement") or (score + comment_count)),
        tags=list(row.get("tags") or []),
        source_metadata=dict(row.get("source_metadata") or {}),
        ingest_run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        ingested_at=datetime.now(timezone.utc).isoformat(),
        snapshot_path=snapshot_path,
    ).to_dict()


def ingest_input(input_path: Path, output_path: Path, source: str = "") -> list[dict[str, Any]]:
    suffix = input_path.suffix.lower()
    if suffix == ".jsonl":
        rows = read_jsonl(input_path)
    elif suffix == ".csv":
        rows = read_csv(input_path)
    else:
        raise ValueError(f"Unsupported input format: {input_path}")

    normalized = [_ingest_row(row, source=source, snapshot_path=str(input_path)) for row in rows]
    write_jsonl(output_path, normalized)
    return normalized


def classify_posts(raw_posts_path: Path, output_path: Path, taxonomy_path: Path) -> list[dict]:
    taxonomy = load_taxonomy(taxonomy_path)
    rows = read_jsonl(raw_posts_path)
    normalized_rows = [row if "post_id" in row else _ingest_row(row, source=str(row.get("source") or ""), snapshot_path=str(raw_posts_path)) for row in rows]
    classified = [classify_post(PostRecord(**row), taxonomy).to_dict() for row in normalized_rows]
    write_jsonl(output_path, classified)
    return classified


def cluster_classified_posts(classified_posts_path: Path, output_path: Path) -> list[dict]:
    rows = read_jsonl(classified_posts_path)
    clusters = cluster_posts(rows)
    write_json(output_path, clusters)
    return clusters


def generate_reports(classified: list[dict], clusters: list[dict], repo_root: Path) -> dict[str, Path]:
    paths = repo_paths(repo_root)
    write_markdown(paths["weekly_market_report"], render_weekly_market_report(classified, clusters))
    write_markdown(paths["quotes"], render_quotes(classified))
    write_markdown(paths["feature_signals"], render_feature_signals(classified, clusters))
    write_markdown(paths["segment_analysis"], render_segment_analysis(classified))
    write_markdown(paths["pricing_notes"], render_pricing_notes(classified))
    return paths


def run_all(input_path: Path, repo_root: Path) -> dict[str, Path]:
    paths = repo_paths(repo_root)
    ingest_input(input_path, paths["raw_posts"])
    classified = classify_posts(paths["raw_posts"], paths["classified_posts"], repo_root / "configs/taxonomy.json")
    clusters = cluster_classified_posts(paths["classified_posts"], paths["theme_clusters"])
    return generate_reports(classified, clusters, repo_root)


def run_reddit_x_batch(
    repo_root: Path,
    post_min_score: int = 3,
    comment_min_score: int = 2,
    focus_path: Path | None = None,
    targets_path: Path | None = None,
    taxonomy_path: Path | None = None,
) -> dict[str, Path]:
    paths = repo_paths(repo_root)

    effective_focus_path = focus_path or (repo_root / "configs/concept_focus.json")
    effective_targets_path = targets_path or (repo_root / "configs/source_targets.json")
    effective_taxonomy_path = taxonomy_path or (repo_root / "configs/taxonomy.json")

    discovery_payload = run_target_discovery(repo_root, targets_path=effective_targets_path, focus_path=effective_focus_path)
    _merge_jsonl_files([paths["imported_reddit_posts"], paths["imported_x_posts"]], paths["merged_posts"])
    _merge_jsonl_files([paths["imported_reddit_comments"], paths["imported_x_comments"]], paths["merged_comments"])

    screened_posts = run_post_screen(paths["merged_posts"], repo_root, min_score=post_min_score, focus_path=effective_focus_path)
    screened_comments = run_comment_screen(paths["merged_comments"], repo_root, min_score=comment_min_score, focus_path=effective_focus_path)

    classified_posts = classify_posts(paths["screened_posts"], paths["classified_screened_posts"], effective_taxonomy_path)
    classified_comments = classify_posts(paths["screened_comments"], paths["classified_screened_comments"], effective_taxonomy_path)

    post_clusters = cluster_classified_posts(paths["classified_screened_posts"], paths["theme_clusters_screened_posts"])
    comment_clusters = cluster_classified_posts(paths["classified_screened_comments"], paths["theme_clusters_screened_comments"])

    combined_classified = classified_posts + classified_comments
    combined_clusters = sorted(post_clusters + comment_clusters, key=lambda cluster: cluster["priority_score"], reverse=True)
    write_markdown(paths["research_summary"], render_research_summary(discovery_payload, screened_posts, screened_comments, classified_posts, classified_comments, post_clusters, comment_clusters))

    for extra_path in [paths["source_discovery_md"], paths["screened_posts_md"], paths["screened_comments_md"]]:
        if extra_path.exists():
            extra_path.unlink()
    return {
        "research_summary": paths["research_summary"],
    }
