from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def choose_theme_label(post: dict) -> str:
    if post.get("trust_concern"):
        return f"trust: {post['trust_concern']}"
    if post.get("pain_point"):
        return f"pain: {post['pain_point']}"
    if post.get("job_to_be_done"):
        return f"job: {post['job_to_be_done']}"
    return "misc: uncategorized"


def cluster_posts(posts: list[dict]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        grouped[choose_theme_label(post)].append(post)

    clusters: list[dict[str, Any]] = []
    for idx, (label, bucket) in enumerate(sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True), start=1):
        segment_counts = Counter(post.get("segment", "") for post in bucket if post.get("segment"))
        tool_counts = Counter(post.get("current_tool", "") for post in bucket if post.get("current_tool"))
        job_counts = Counter(post.get("job_to_be_done", "") for post in bucket if post.get("job_to_be_done"))
        pain_counts = Counter(post.get("pain_point", "") for post in bucket if post.get("pain_point"))
        trust_counts = Counter(post.get("trust_concern", "") for post in bucket if post.get("trust_concern"))
        feature_counts = Counter(post.get("feature_implication", "") for post in bucket if post.get("feature_implication"))
        messaging_counts = Counter(post.get("messaging_implication", "") for post in bucket if post.get("messaging_implication"))

        post_count = len(bucket)
        avg_pain = round(sum(post.get("pain_intensity", 0) for post in bucket) / post_count, 2)
        avg_engagement = round(sum(float(post.get("engagement", 0)) for post in bucket) / post_count, 2)
        avg_wtp = round(sum(post.get("willingness_to_pay_score", 0) for post in bucket) / post_count, 2)
        avg_fit = round(sum(post.get("fit_score", 0) for post in bucket) / post_count, 2)
        frequency_score = min(post_count, 5)
        priority_score = round((frequency_score * 0.3) + (avg_pain * 0.25) + (avg_wtp * 0.2) + (avg_fit * 0.25), 2)

        clusters.append(
            {
                "theme_id": f"T{idx:03d}",
                "theme_label": label,
                "post_count": post_count,
                "frequency_score": frequency_score,
                "avg_pain_intensity": avg_pain,
                "avg_engagement": avg_engagement,
                "avg_willingness_to_pay": avg_wtp,
                "avg_fit_score": avg_fit,
                "priority_score": priority_score,
                "dominant_segments": [item for item, _ in segment_counts.most_common(3)],
                "dominant_tools": [item for item, _ in tool_counts.most_common(3)],
                "jobs": [item for item, _ in job_counts.most_common(3)],
                "pains": [item for item, _ in pain_counts.most_common(3)],
                "trust_concerns": [item for item, _ in trust_counts.most_common(3)],
                "feature_implications": [item for item, _ in feature_counts.most_common(3)],
                "messaging_implications": [item for item, _ in messaging_counts.most_common(3)],
                "example_urls": [post.get("url", "") for post in bucket[:5] if post.get("url")],
            }
        )

    return sorted(clusters, key=lambda cluster: cluster["priority_score"], reverse=True)

