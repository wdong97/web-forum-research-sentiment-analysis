# WFRS

WFRS is a config-driven thread research and sentiment analysis pipeline for Reddit, X, forums, app reviews, and other public discussion sources.

It is built for people who want to:

- collect public threads or exported discussions
- screen for relevance to a topic, market, product, or narrative
- extract sentiment, pain points, objections, trust concerns, and buying signals
- cluster recurring themes
- generate one source-linked research summary instead of a pile of ad hoc notes

## Core Workflow

1. pick a research profile
2. collect exports or public thread dumps
3. import them into a common JSONL format
4. screen posts and comments for relevance
5. classify the retained items
6. cluster themes
7. generate one consolidated markdown summary with provenance

The current default profile is a Personalized OS example, but the repo is reusable across other research tasks by swapping config files.

## What The Repo Supports

- Reddit thread import from JSON exports
- bulk Reddit directory import
- X post and reply import from JSON, JSONL, or CSV exports
- bulk X directory import
- concept-focused screening for posts and comments
- deterministic first-pass classification
- theme clustering
- one-shot batch execution over imported Reddit/X data

## Installation

Create a local environment:

```bash
UV_CACHE_DIR=.uv-cache uv venv .venv
```

Run commands with:

```bash
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli <command>
```

## Quick Start

If you already have export directories:

```bash
pos-research import-reddit-dir --input-dir path/to/reddit_exports
pos-research import-x-dir --input-dir path/to/x_exports
pos-research run-reddit-x-batch
```

The main output is:

- `reports/staging/research-summary.md`

## CLI

```bash
pos-research import-reddit-thread --input path/to/thread.json
pos-research import-reddit-dir --input-dir path/to/reddit_exports
pos-research import-x-export --input path/to/x_export.json
pos-research import-x-dir --input-dir path/to/x_exports
pos-research discover-targets --focus-config configs/concept_focus.json --targets-config configs/source_targets.json
pos-research screen-posts --input path/to/posts.jsonl --focus-config configs/concept_focus.json
pos-research screen-comments --input path/to/comments.jsonl --focus-config configs/concept_focus.json
pos-research classify --input path/to/items.jsonl --output path/to/classified.jsonl --taxonomy-config configs/taxonomy.json
pos-research cluster --input path/to/classified.jsonl --output path/to/clusters.json
pos-research run-reddit-x-batch --focus-config configs/concept_focus.json --targets-config configs/source_targets.json --taxonomy-config configs/taxonomy.json
```

## Research Profiles

To repurpose the pipeline for another market or topic, swap:

- `--focus-config`
- `--targets-config`
- `--taxonomy-config`

That lets you reuse the same import, screening, classification, and reporting flow for:

- market research
- product discovery
- competitor sentiment tracking
- policy / narrative monitoring
- community research

## Scale

This repo is designed to scale through imports, not fragile live scraping.

For 1k to 10k+ items, the practical path is:

1. collect Reddit thread exports and X reply exports in directories
2. run `import-reddit-dir` and `import-x-dir`
3. run `run-reddit-x-batch`

In constrained environments, direct public API access may be blocked or rate-limited. Export-driven ingestion is the stable path.

## Data Model

The canonical internal format is JSONL.

The pipeline stores:

- imported post/comment feeds
- screened subsets
- classified items
- clustered themes
- one final source-linked markdown report

CSV import is also supported when fields can be mapped into the common schema.

## Output Philosophy

The repo intentionally favors:

- inspectable intermediate files
- explicit provenance
- one canonical report for synthesis

instead of:

- hidden processing
- black-box scoring only
- many overlapping summary documents

## Docs

- import formats: [`docs/import-formats.md`](docs/import-formats.md)
- pipeline flow: [`docs/pipeline-flow.md`](docs/pipeline-flow.md)
- schema: [`docs/schema.md`](docs/schema.md)

## Notes

- The example configs and seeds in this repo are centered on one research case, but the tool itself is generic.
- Generated data and research outputs are gitignored so the repo stays publishable and reusable.
