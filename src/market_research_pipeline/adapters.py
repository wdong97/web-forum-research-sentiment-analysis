from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .storage import read_csv, read_json, read_jsonl, write_jsonl


def _ensure_list(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ["data", "results", "tweets", "posts", "items", "comments"]:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def _string(value: Any) -> str:
    return "" if value is None else str(value)


def _reddit_permalink(value: str) -> str:
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"https://www.reddit.com{value}"


def _reddit_post_row(item: dict, snapshot_path: str) -> dict:
    title = _string(item.get("title"))
    body = _string(item.get("selftext") or item.get("body") or item.get("content"))
    permalink = _reddit_permalink(_string(item.get("permalink") or item.get("url")))
    subreddit = _string(item.get("subreddit") or item.get("subreddit_name_prefixed")).replace("r/", "")
    return {
        "id": _string(item.get("id") or item.get("name")),
        "source": "reddit",
        "source_type": "post",
        "thread_id": _string(item.get("id") or item.get("link_id")),
        "url": permalink,
        "created_at": _string(item.get("created_utc") or item.get("created_at")),
        "author": _string(item.get("author")),
        "title": title,
        "body": body,
        "raw_text": body or title,
        "score": item.get("score") or 0,
        "comment_count": item.get("num_comments") or item.get("comment_count") or 0,
        "engagement": (item.get("score") or 0) + (item.get("num_comments") or item.get("comment_count") or 0),
        "tags": [subreddit] if subreddit else [],
        "source_metadata": {
            "adapter": "reddit_thread",
            "subreddit": subreddit,
            "capture_method": "import_adapter",
            "original_kind": "post",
            "snapshot_path": snapshot_path,
        },
    }


def _reddit_comment_row(item: dict, snapshot_path: str, default_thread_id: str = "", parent_post: dict | None = None) -> dict:
    body = _string(item.get("body") or item.get("content"))
    permalink = _reddit_permalink(_string(item.get("permalink")))
    subreddit = _string(item.get("subreddit") or item.get("subreddit_name_prefixed")).replace("r/", "")
    parent_title = _string((parent_post or {}).get("title"))
    parent_body = _string((parent_post or {}).get("selftext") or (parent_post or {}).get("body"))
    return {
        "id": _string(item.get("id") or item.get("name")),
        "source": "reddit",
        "source_type": "comment",
        "thread_id": _string(item.get("link_id") or default_thread_id),
        "url": permalink,
        "created_at": _string(item.get("created_utc") or item.get("created_at")),
        "author": _string(item.get("author")),
        "title": "",
        "body": body,
        "raw_text": body,
        "parent_title": parent_title,
        "parent_body": parent_body,
        "score": item.get("score") or 0,
        "comment_count": item.get("replies_count") or 0,
        "engagement": (item.get("score") or 0) + (item.get("replies_count") or 0),
        "tags": [subreddit] if subreddit else [],
        "source_metadata": {
            "adapter": "reddit_thread",
            "subreddit": subreddit,
            "capture_method": "import_adapter",
            "original_kind": "comment",
            "snapshot_path": snapshot_path,
        },
    }


def import_reddit_thread(input_path: Path, posts_output: Path, comments_output: Path) -> tuple[list[dict], list[dict]]:
    payload = read_json(input_path)
    rows = _ensure_list(payload)
    posts: list[dict] = []
    comments: list[dict] = []

    if len(rows) == 2 and all(isinstance(item.get("data", {}).get("children"), list) for item in rows if isinstance(item, dict)):
        post_children = rows[0]["data"]["children"]
        comment_children = rows[1]["data"]["children"]
        parent_post = post_children[0]["data"] if post_children else {}
        if parent_post:
            posts.append(_reddit_post_row(parent_post, str(input_path)))
        for child in comment_children:
            data = child.get("data", {})
            if data.get("body"):
                comments.append(_reddit_comment_row(data, str(input_path), default_thread_id=_string(parent_post.get("id")), parent_post=parent_post))
    else:
        parent_post = next((row for row in rows if row.get("title")), {})
        for row in rows:
            if row.get("title"):
                posts.append(_reddit_post_row(row, str(input_path)))
            elif row.get("body"):
                comments.append(_reddit_comment_row(row, str(input_path), default_thread_id=_string(parent_post.get("id")), parent_post=parent_post))

    write_jsonl(posts_output, posts)
    write_jsonl(comments_output, comments)
    return posts, comments


def import_reddit_dir(input_dir: Path, posts_output: Path, comments_output: Path) -> tuple[list[dict], list[dict]]:
    posts: list[dict] = []
    comments: list[dict] = []
    for path in sorted(input_dir.rglob("*.json")):
        imported_posts, imported_comments = import_reddit_thread(path, posts_output, comments_output)
        posts.extend(imported_posts)
        comments.extend(imported_comments)
    write_jsonl(posts_output, posts)
    write_jsonl(comments_output, comments)
    return posts, comments


def _x_post_row(item: dict, snapshot_path: str) -> dict:
    text = _string(item.get("full_text") or item.get("text") or item.get("body") or item.get("content"))
    post_id = _string(item.get("id") or item.get("tweet_id") or item.get("rest_id"))
    handle = _string(item.get("username") or item.get("screen_name") or item.get("author_handle"))
    url = _string(item.get("url"))
    if not url and handle and post_id:
        url = f"https://x.com/{handle}/status/{post_id}"
    return {
        "id": post_id,
        "source": "x",
        "source_type": "post",
        "thread_id": _string(item.get("conversation_id") or item.get("in_reply_to_status_id") or item.get("parent_post_id") or post_id),
        "url": url,
        "created_at": _string(item.get("created_at")),
        "author": _string(item.get("author_name") or item.get("name") or handle),
        "author_handle": handle,
        "title": _string(item.get("title")),
        "body": text,
        "raw_text": text,
        "score": item.get("favorite_count") or item.get("like_count") or 0,
        "comment_count": item.get("reply_count") or 0,
        "engagement": (item.get("favorite_count") or item.get("like_count") or 0) + (item.get("reply_count") or 0) + (item.get("retweet_count") or 0),
        "tags": ["x"],
        "source_metadata": {
            "adapter": "x_export",
            "capture_method": "import_adapter",
            "snapshot_path": snapshot_path,
        },
    }


def _x_comment_row(item: dict, snapshot_path: str) -> dict:
    row = _x_post_row(item, snapshot_path)
    row["source_type"] = "comment"
    row["parent_title"] = _string(item.get("parent_title"))
    row["parent_body"] = _string(item.get("parent_body"))
    row["source_metadata"]["original_kind"] = "reply"
    return row


def import_x_export(input_path: Path, posts_output: Path, comments_output: Path) -> tuple[list[dict], list[dict]]:
    if input_path.suffix.lower() == ".csv":
        rows = read_csv(input_path)
    elif input_path.suffix.lower() == ".jsonl":
        rows = read_jsonl(input_path)
    else:
        rows = _ensure_list(read_json(input_path))

    posts: list[dict] = []
    comments: list[dict] = []
    for row in rows:
        kind = _string(row.get("record_type") or row.get("type") or row.get("tweet_type")).lower()
        if kind in {"reply", "comment"} or row.get("in_reply_to_status_id") or row.get("parent_post_id"):
            comments.append(_x_comment_row(row, str(input_path)))
        else:
            posts.append(_x_post_row(row, str(input_path)))

    write_jsonl(posts_output, posts)
    write_jsonl(comments_output, comments)
    return posts, comments


def import_x_dir(input_dir: Path, posts_output: Path, comments_output: Path) -> tuple[list[dict], list[dict]]:
    posts: list[dict] = []
    comments: list[dict] = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".jsonl", ".csv"}:
            continue
        imported_posts, imported_comments = import_x_export(path, posts_output, comments_output)
        posts.extend(imported_posts)
        comments.extend(imported_comments)
    write_jsonl(posts_output, posts)
    write_jsonl(comments_output, comments)
    return posts, comments
