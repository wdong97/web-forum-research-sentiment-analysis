from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import (
    classify_posts,
    cluster_classified_posts,
    generate_reports,
    ingest_input,
    repo_paths,
    run_comment_screen,
    run_all,
    run_reddit_x_batch,
    run_reddit_import,
    run_reddit_dir_import,
    run_post_screen,
    run_target_discovery,
    run_x_dir_import,
    run_x_import,
)
from .storage import read_json, read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personalized OS market research pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Normalize input into raw_posts.jsonl")
    ingest.add_argument("--input", required=True)
    ingest.add_argument("--source", default="")

    reddit_import = subparsers.add_parser("import-reddit-thread", help="Import a Reddit thread export into post/comment JSONL files")
    reddit_import.add_argument("--input", required=True)

    reddit_import_dir = subparsers.add_parser("import-reddit-dir", help="Import a directory of Reddit thread exports")
    reddit_import_dir.add_argument("--input-dir", required=True)

    x_import = subparsers.add_parser("import-x-export", help="Import an X export into post/comment JSONL files")
    x_import.add_argument("--input", required=True)

    x_import_dir = subparsers.add_parser("import-x-dir", help="Import a directory of X exports")
    x_import_dir.add_argument("--input-dir", required=True)

    discover = subparsers.add_parser("discover-targets", help="Materialize curated Reddit/X source targets")
    discover.add_argument("--targets-config", default="configs/source_targets.json")
    discover.add_argument("--focus-config", default="configs/concept_focus.json")

    screen_posts = subparsers.add_parser("screen-posts", help="Filter candidate posts against the Personalized OS concept focus")
    screen_posts.add_argument("--input", required=True)
    screen_posts.add_argument("--min-score", type=int, default=3)
    screen_posts.add_argument("--focus-config", default="configs/concept_focus.json")

    screen_comments = subparsers.add_parser("screen-comments", help="Filter candidate comments against the Personalized OS concept focus")
    screen_comments.add_argument("--input", required=True)
    screen_comments.add_argument("--min-score", type=int, default=2)
    screen_comments.add_argument("--focus-config", default="configs/concept_focus.json")

    classify = subparsers.add_parser("classify", help="Classify normalized posts")
    classify.add_argument("--input", default="data/normalized/raw_posts.jsonl")
    classify.add_argument("--output", default="data/processed/classified_posts.jsonl")
    classify.add_argument("--taxonomy-config", default="configs/taxonomy.json")

    cluster = subparsers.add_parser("cluster", help="Cluster classified posts")
    cluster.add_argument("--input", default="data/processed/classified_posts.jsonl")
    cluster.add_argument("--output", default="data/processed/theme_clusters.json")

    report = subparsers.add_parser("report", help="Generate markdown reports")
    report.add_argument("--input", default="data/processed/classified_posts.jsonl")
    report.add_argument("--clusters", default="data/processed/theme_clusters.json")

    run = subparsers.add_parser("run-all", help="Run ingest, classify, cluster, and report")
    run.add_argument("--input", required=True)

    reddit_x_batch = subparsers.add_parser("run-reddit-x-batch", help="Merge imported Reddit/X files and run the full concept-screened batch")
    reddit_x_batch.add_argument("--post-min-score", type=int, default=3)
    reddit_x_batch.add_argument("--comment-min-score", type=int, default=2)
    reddit_x_batch.add_argument("--focus-config", default="configs/concept_focus.json")
    reddit_x_batch.add_argument("--targets-config", default="configs/source_targets.json")
    reddit_x_batch.add_argument("--taxonomy-config", default="configs/taxonomy.json")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path.cwd()
    paths = repo_paths(repo_root)

    if args.command == "ingest":
        ingest_input(Path(args.input), paths["raw_posts"], source=args.source)
        print(paths["raw_posts"])
        return

    if args.command == "import-reddit-thread":
        run_reddit_import(Path(args.input), repo_root)
        print(paths["imported_reddit_posts"])
        print(paths["imported_reddit_comments"])
        return

    if args.command == "import-reddit-dir":
        run_reddit_dir_import(Path(args.input_dir), repo_root)
        print(paths["imported_reddit_posts"])
        print(paths["imported_reddit_comments"])
        return

    if args.command == "import-x-export":
        run_x_import(Path(args.input), repo_root)
        print(paths["imported_x_posts"])
        print(paths["imported_x_comments"])
        return

    if args.command == "import-x-dir":
        run_x_dir_import(Path(args.input_dir), repo_root)
        print(paths["imported_x_posts"])
        print(paths["imported_x_comments"])
        return

    if args.command == "discover-targets":
        run_target_discovery(repo_root, targets_path=Path(args.targets_config), focus_path=Path(args.focus_config))
        print(paths["source_discovery_md"])
        return

    if args.command == "screen-posts":
        run_post_screen(Path(args.input), repo_root, min_score=args.min_score, focus_path=Path(args.focus_config))
        print(paths["screened_posts"])
        return

    if args.command == "screen-comments":
        run_comment_screen(Path(args.input), repo_root, min_score=args.min_score, focus_path=Path(args.focus_config))
        print(paths["screened_comments"])
        return

    if args.command == "classify":
        classify_posts(Path(args.input), Path(args.output), Path(args.taxonomy_config))
        print(Path(args.output))
        return

    if args.command == "cluster":
        cluster_classified_posts(Path(args.input), Path(args.output))
        print(Path(args.output))
        return

    if args.command == "report":
        classified = read_jsonl(Path(args.input))
        clusters = read_json(Path(args.clusters))
        generate_reports(classified, clusters, repo_root)
        print(paths["weekly_market_report"])
        return

    if args.command == "run-all":
        generated = run_all(Path(args.input), repo_root)
        for path in generated.values():
            print(path)
        return

    if args.command == "run-reddit-x-batch":
        generated = run_reddit_x_batch(
            repo_root,
            post_min_score=args.post_min_score,
            comment_min_score=args.comment_min_score,
            focus_path=Path(args.focus_config),
            targets_path=Path(args.targets_config),
            taxonomy_path=Path(args.taxonomy_config),
        )
        for path in generated.values():
            print(path)


if __name__ == "__main__":
    main()
