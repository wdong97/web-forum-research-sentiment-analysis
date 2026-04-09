from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone


def _top(counter: Counter, limit: int = 5) -> list[tuple[str, int]]:
    return [(item, count) for item, count in counter.most_common(limit) if item]


def render_weekly_market_report(posts: list[dict], clusters: list[dict]) -> str:
    segment_counts = Counter(post.get("segment", "") for post in posts)
    pain_counts = Counter(post.get("pain_point", "") for post in posts)
    trust_counts = Counter(post.get("trust_concern", "") for post in posts)
    message_counts = Counter(post.get("messaging_implication", "") for post in posts)

    strongest_segment = _top(segment_counts, 1)
    strongest_segment_label = strongest_segment[0][0] if strongest_segment else "unknown"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Weekly Market Report",
        "",
        f"_Generated {timestamp}_",
        "",
        "## Executive Read",
        "",
        f"The current sample leans most strongly toward **{strongest_segment_label}**. Demand clusters around source-grounded synthesis, context continuity, and lower-friction workflows rather than generic sentiment or broad 'AI OS' positioning.",
        "",
        "Trust and setup objections recur often enough that the product should continue to lead with selective ingest, reviewability, and visible provenance.",
        "",
        "## What The Sample Is Suggesting",
        "",
    ]
    for cluster in clusters[:5]:
        lines.append(
            f"- **{cluster['theme_label']}**: {cluster['post_count']} posts, priority {cluster['priority_score']}, segments: {', '.join(cluster['dominant_segments']) or 'n/a'}."
        )

    lines.extend(
        [
            "",
            "## Strongest Demand Signals",
            "",
        ]
    )
    for label, count in _top(pain_counts):
        lines.append(f"- Pain signal: **{label}** ({count})")
    lines.extend(["", "## Trust And Objection Signals", ""])
    for label, count in _top(trust_counts):
        lines.append(f"- Trust signal: **{label}** ({count})")
    lines.extend(["", "## Messaging Angles", ""])
    for label, count in _top(message_counts):
        lines.append(f"- {label} ({count})")
    lines.extend(
        [
            "",
            "## Preliminary Wedge View",
            "",
            "The strongest immediate wedge looks like second-brain power users, with small-team operators close behind. Creators remain strategically attractive because the workflow can be more differentiated, but the current public-discussion sample shows a clearer and denser signal around knowledge-work and context-management pain.",
            "",
            "## Next Data To Ingest",
            "",
            "- More Reddit and HN threads on Obsidian, NotebookLM, Tana, Mem, Granola, and AI note/memory tools",
            "- App reviews or discussion threads where users compare privacy, setup friction, and grounding quality",
            "- Creator workflows where context continuity, release planning, and brand memory are explicit",
            "- Small-team operator discussions around follow-up tracking, shared context, and proposal/client memory",
        ]
    )
    return "\n".join(lines) + "\n"


def render_quotes(posts: list[dict]) -> str:
    ranked = sorted(posts, key=lambda post: (post.get("pain_intensity", 0), post.get("fit_score", 0), post.get("engagement", 0)), reverse=True)
    lines = ["# Quotes", "", "Short excerpts from the current sample with direct source links.", ""]
    for post in ranked[:12]:
        quote = post.get("useful_quote", "").strip()
        if not quote:
            continue
        lines.append(f"## {post.get('source', 'source').title()} | {post.get('segment', 'unknown')}")
        lines.append("")
        lines.append(f"> {quote}")
        lines.append("")
        lines.append(f"Source: {post.get('url', '')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_feature_signals(posts: list[dict], clusters: list[dict]) -> str:
    feature_counts = Counter(post.get("feature_implication", "") for post in posts)
    lines = ["# Feature Signals", "", "## Highest-Signal Implications", ""]
    for label, count in _top(feature_counts, 8):
        lines.append(f"- {label} ({count})")
    lines.extend(["", "## Top Themes", ""])
    for cluster in clusters[:5]:
        lines.append(f"- {cluster['theme_label']}: {', '.join(cluster['feature_implications'])}")
    return "\n".join(lines) + "\n"


def render_segment_analysis(posts: list[dict]) -> str:
    by_segment: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        by_segment[post.get("segment", "unknown")].append(post)

    lines = ["# Segment Analysis", ""]
    for segment, bucket in sorted(by_segment.items(), key=lambda item: len(item[1]), reverse=True):
        pain_counts = Counter(post.get("pain_point", "") for post in bucket)
        trust_counts = Counter(post.get("trust_concern", "") for post in bucket)
        avg_fit = round(sum(post.get("fit_score", 0) for post in bucket) / len(bucket), 2)
        avg_wtp = round(sum(post.get("willingness_to_pay_score", 0) for post in bucket) / len(bucket), 2)
        lines.append(f"## {segment}")
        lines.append("")
        lines.append(f"- Sample size: {len(bucket)}")
        lines.append(f"- Avg fit score: {avg_fit}")
        lines.append(f"- Avg willingness-to-pay score: {avg_wtp}")
        for label, count in _top(pain_counts, 3):
            lines.append(f"- Top pain: {label} ({count})")
        for label, count in _top(trust_counts, 2):
            lines.append(f"- Top trust concern: {label} ({count})")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_pricing_notes(posts: list[dict]) -> str:
    wtp_counts = Counter(post.get("willingness_to_pay_score", 0) for post in posts)
    lines = [
        "# Pricing And Economics Notes",
        "",
        "This first pass is based on willingness-to-pay signals inferred from public discussion, not direct pricing interviews.",
        "",
        "## Signal Distribution",
        "",
    ]
    for score, count in sorted(wtp_counts.items(), reverse=True):
        lines.append(f"- WTP score {score}: {count} posts")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Small-team operator discussion tends to support the strongest monetizable wedge because the pain maps more cleanly to saved time and coordination.",
            "- Second-brain power users show strong fit and recurring need, but some of that demand may remain hobbyist or tool-curious unless the workflow is obvious quickly.",
            "- Creator demand looks promising as a differentiated workflow wedge, but pricing proof likely needs real pilot usage rather than broad public sentiment alone.",
            "",
            "## Current Pricing Hypothesis",
            "",
            "- B2C workflow SKU: roughly low-teens per month if the first job is obvious and reviewable",
            "- Prosumer/power tier: higher if ingestion volume, richer models, or premium workflows are included",
            "- Small-team pilot: separate pilot pricing tied to clarity, follow-through, and time saved",
        ]
    )
    return "\n".join(lines) + "\n"


def render_screening_summary(rows: list[dict], stage: str) -> str:
    by_source = Counter(row.get("source", "") for row in rows)
    by_hit = Counter(hit for row in rows for hit in row.get("concept_hits", []))
    ranked = sorted(rows, key=lambda row: (row.get("concept_relevance_score", 0), row.get("score", 0), row.get("comment_count", 0)), reverse=True)
    lines = [
        f"# {stage.title()} Screening Summary",
        "",
        f"- Screened items kept: {len(rows)}",
        "",
        "## Source Mix",
        "",
    ]
    for label, count in by_source.most_common():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Strongest Concept Hits", ""])
    for label, count in by_hit.most_common(8):
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Highest-Priority Items", ""])
    for row in ranked[:10]:
        lines.append(
            f"- [{row.get('title') or row.get('parent_title') or row.get('id')}]({row.get('url','')}) | score {row.get('concept_relevance_score', 0)} | {row.get('screen_reason', '')}"
        )
    lines.append("")
    return "\n".join(lines)


def render_public_sentiment_summary(posts: list[dict], comments: list[dict], post_clusters: list[dict], comment_clusters: list[dict]) -> str:
    all_rows = posts + comments
    segment_counts = Counter(row.get("segment", "") for row in all_rows if row.get("segment"))
    pain_counts = Counter(row.get("pain_point", "") for row in all_rows if row.get("pain_point"))
    trust_counts = Counter(row.get("trust_concern", "") for row in all_rows if row.get("trust_concern"))
    feature_counts = Counter(row.get("feature_implication", "") for row in all_rows if row.get("feature_implication"))
    ranked_quotes = sorted(
        all_rows,
        key=lambda row: (row.get("fit_score", 0), row.get("pain_intensity", 0), row.get("engagement", 0)),
        reverse=True,
    )

    lines = [
        "# Public Sentiment Summary",
        "",
        "_Generated from the current Reddit/X batch focused on the core Personalized OS concept._",
        "",
        "## Bottom Line",
        "",
        "The strongest public signal is for a trustworthy context layer that reduces scatter, shows its work, and stays reviewable. Demand is clearer around grounded briefs, structured summaries, searchable context, and controlled memory behavior than around broad 'AI OS' category language.",
        "",
        "## Highest-Signal Findings",
        "",
    ]

    for cluster in (post_clusters + comment_clusters)[:6]:
        example_link = cluster["example_urls"][0] if cluster.get("example_urls") else ""
        lines.append(
            f"- **{cluster['theme_label']}**: priority {cluster['priority_score']}, segments: {', '.join(cluster['dominant_segments']) or 'n/a'}. Source: {example_link}"
        )

    lines.extend(["", "## Segment Read", ""])
    for label, count in segment_counts.most_common(4):
        lines.append(f"- {label}: {count} items")

    lines.extend(["", "## Recurrent Pains", ""])
    for label, count in pain_counts.most_common(5):
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Recurrent Trust Concerns", ""])
    for label, count in trust_counts.most_common(5):
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Feature Implications", ""])
    for label, count in feature_counts.most_common(5):
        lines.append(f"- {label} ({count})")

    lines.extend(["", "## Representative Source-Linked Evidence", ""])
    used_urls: set[str] = set()
    for row in ranked_quotes:
        url = row.get("url", "")
        quote = row.get("useful_quote", "").strip()
        if not url or not quote or url in used_urls:
            continue
        used_urls.add(url)
        lines.append(f"- {quote} Source: {url}")
        if len(used_urls) >= 8:
            break

    lines.extend(
        [
            "",
            "## Current Recommendation",
            "",
            "- Lead with selective ingest, source-linked answers, and reviewable updates.",
            "- Package value as concrete workflows like briefs, summaries, continuity, and what-matters-now views.",
            "- Keep setup low and avoid asking users to build a complicated system before the first payoff.",
            "- Treat privacy, provenance, and checkpoints as core product behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def render_research_summary(
    discovery_payload: dict,
    screened_posts: list[dict],
    screened_comments: list[dict],
    classified_posts: list[dict],
    classified_comments: list[dict],
    post_clusters: list[dict],
    comment_clusters: list[dict],
) -> str:
    all_classified = classified_posts + classified_comments
    segment_counts = Counter(row.get("segment", "") for row in all_classified if row.get("segment"))
    pain_counts = Counter(row.get("pain_point", "") for row in all_classified if row.get("pain_point"))
    trust_counts = Counter(row.get("trust_concern", "") for row in all_classified if row.get("trust_concern"))
    feature_counts = Counter(row.get("feature_implication", "") for row in all_classified if row.get("feature_implication"))
    target_count = len(discovery_payload["targets"]["reddit"]) + len(discovery_payload["targets"]["x"])

    lines = [
        "# Research Summary",
        "",
        f"_Focus: {discovery_payload['focus_name']}_",
        "",
        "## Scope",
        "",
        f"- Discovery targets: {target_count}",
        f"- Screened posts kept: {len(screened_posts)}",
        f"- Screened comments kept: {len(screened_comments)}",
        f"- Classified items: {len(all_classified)}",
        "",
        "## Constraints",
        "",
        "- Public Reddit API access is blocked in this environment, so high-volume live pulls require exports or authenticated collection outside this session.",
        "- The repo is now structured to ingest large Reddit/X export directories so the same workflow can scale to 1k to 10k+ items when exports are available.",
        "",
        "## Discovery Targets",
        "",
    ]

    for group_name in ["reddit", "x"]:
        lines.append(f"### {group_name.title()}")
        lines.append("")
        for target in discovery_payload["targets"][group_name]:
            lines.append(f"- **{target['name']}** ({target['priority']}): {target['rationale']} {target['url']}")
        lines.append("")

    lines.extend(["## Post Screening", ""])
    ranked_posts = sorted(screened_posts, key=lambda row: (row.get("concept_relevance_score", 0), row.get("score", 0), row.get("comment_count", 0)), reverse=True)
    for row in ranked_posts[:15]:
        lines.append(f"- [{row.get('title') or row.get('id')}]({row.get('url','')}) | score {row.get('concept_relevance_score', 0)} | {row.get('screen_reason', '')}")

    lines.extend(["", "## Comment Screening", ""])
    ranked_comments = sorted(screened_comments, key=lambda row: (row.get("concept_relevance_score", 0), row.get("score", 0), row.get("comment_count", 0)), reverse=True)
    for row in ranked_comments[:15]:
        lines.append(f"- [{row.get('parent_title') or row.get('id')}]({row.get('url','')}) | score {row.get('concept_relevance_score', 0)} | {row.get('screen_reason', '')}")

    lines.extend(["", "## Highest-Signal Findings", ""])
    for cluster in sorted(post_clusters + comment_clusters, key=lambda cluster: cluster["priority_score"], reverse=True)[:10]:
        source = cluster["example_urls"][0] if cluster.get("example_urls") else ""
        lines.append(f"- **{cluster['theme_label']}**: priority {cluster['priority_score']}, segments: {', '.join(cluster['dominant_segments']) or 'n/a'}. Source: {source}")

    lines.extend(["", "## Segment Read", ""])
    for label, count in segment_counts.most_common(6):
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Recurrent Pains", ""])
    for label, count in pain_counts.most_common(8):
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Recurrent Trust Concerns", ""])
    for label, count in trust_counts.most_common(8):
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Feature Implications", ""])
    for label, count in feature_counts.most_common(8):
        lines.append(f"- {label} ({count})")

    lines.extend(["", "## Representative Evidence", ""])
    used_urls: set[str] = set()
    for row in sorted(all_classified, key=lambda row: (row.get("fit_score", 0), row.get("pain_intensity", 0), row.get("engagement", 0)), reverse=True):
        url = row.get("url", "")
        quote = row.get("useful_quote", "").strip()
        if not quote or not url or url in used_urls:
            continue
        used_urls.add(url)
        lines.append(f"- {quote} Source: {url}")
        if len(used_urls) >= 15:
            break

    lines.extend(
        [
            "",
            "## Current Recommendation",
            "",
            "- Lead with selective ingest, source-linked answers, and reviewable updates.",
            "- Package value as concrete workflows like briefs, continuity, summaries, and what-matters-now views.",
            "- Keep setup low and avoid asking users to build a complicated system before the first payoff.",
            "- Treat privacy, provenance, and checkpoints as core product behavior.",
            "",
        ]
    )
    return "\n".join(lines)
