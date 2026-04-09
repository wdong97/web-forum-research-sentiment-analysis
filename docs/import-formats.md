# Import Formats

## Reddit Thread Export

Supported shapes:

- Reddit-style thread JSON with two top-level listing objects:
  - first listing contains the post
  - second listing contains comments
- Flat JSON array with mixed post/comment dicts

Preferred fields:

- post: `id`, `title`, `selftext`, `author`, `created_utc`, `score`, `num_comments`, `subreddit`, `permalink`
- comment: `id`, `body`, `author`, `created_utc`, `score`, `subreddit`, `permalink`, `link_id`

CLI:

```bash
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli import-reddit-thread \
  --input path/to/thread.json
```

Outputs:

- `data/imports/reddit_posts.jsonl`
- `data/imports/reddit_comments.jsonl`

## X Export

Supported shapes:

- JSON array
- JSON object with `data` / `results` / `tweets` / `posts`
- JSONL
- CSV

Preferred fields:

- post/reply: `id` or `tweet_id`, `text` or `full_text`, `created_at`, `username` or `screen_name`, `favorite_count` or `like_count`, `reply_count`
- reply detection: `record_type=reply`, `type=reply`, `tweet_type=reply`, `in_reply_to_status_id`, or `parent_post_id`

CLI:

```bash
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli import-x-export \
  --input path/to/x_export.json
```

Outputs:

- `data/imports/x_posts.jsonl`
- `data/imports/x_comments.jsonl`

## Recommended Weekly Flow

1. Import Reddit thread exports
2. Import X post/reply exports
3. Run `screen-posts` on imported posts
4. Run `screen-comments` on imported comments
5. Run `classify`
6. Run `cluster`
7. Refresh markdown summaries

Or run the full batch:

```bash
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli run-reddit-x-batch
```

## Directory Imports

For higher-volume weekly runs:

```bash
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli import-reddit-dir --input-dir path/to/reddit_exports
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli import-x-dir --input-dir path/to/x_exports
PYTHONPATH=src .venv/bin/python -m market_research_pipeline.cli run-reddit-x-batch
```
