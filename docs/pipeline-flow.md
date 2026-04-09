# Pipeline Flow

```mermaid
flowchart TD
    A[Choose research profile\nfocus + targets + taxonomy] --> B[Collect exports\nReddit threads / X posts+replies / forum exports]
    B --> C1[import-reddit-thread or import-reddit-dir]
    B --> C2[import-x-export or import-x-dir]
    B --> C3[import-hn-algolia or import-discourse-topic]
    C1 --> D1[data/imports/reddit_posts.jsonl]
    C1 --> D2[data/imports/reddit_comments.jsonl]
    C2 --> D3[data/imports/x_posts.jsonl]
    C2 --> D4[data/imports/x_comments.jsonl]
    C3 --> D5[data/imports/forum_posts.jsonl]
    C3 --> D6[data/imports/forum_comments.jsonl]
    D1 --> E[run-reddit-x-batch]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    E --> F[merge imports]
    F --> G[screen posts + comments]
    G --> H[classify jobs pains objections trust]
    H --> I[cluster themes]
    I --> J[write one research summary]
    J --> K[optional vault sink or external publishing]
```

## Notes

- The import step is where scale happens. With enough export files, the same batch path can handle 1k to 10k+ items.
- The batch path intentionally writes one main report: `reports/staging/research-summary.md`.
- Profile reuse comes from swapping focus, target, and taxonomy config files.
