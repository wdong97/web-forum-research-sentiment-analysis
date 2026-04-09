# Common Schema

Each normalized post record uses this shape:

- `post_id`
- `source`
- `source_type`
- `thread_id`
- `url`
- `created_at`
- `author`
- `author_handle`
- `title`
- `body`
- `raw_text`
- `lang`
- `score`
- `comment_count`
- `engagement`
- `tags`
- `source_metadata`
- `ingest_run_id`
- `ingested_at`
- `snapshot_path`

Classification fields:

- `job_to_be_done`
- `pain_point`
- `desire`
- `objection`
- `trust_concern`
- `current_tool`
- `segment`
- `buying_signal`
- `sentiment`
- `useful_quote`
- `feature_implication`
- `messaging_implication`
- `switching_trigger`
- `pain_intensity`
- `willingness_to_pay_score`
- `fit_score`

Theme cluster fields:

- `theme_id`
- `theme_label`
- `post_count`
- `frequency_score`
- `avg_pain_intensity`
- `avg_engagement`
- `avg_willingness_to_pay`
- `avg_fit_score`
- `priority_score`
- `dominant_segments`
- `dominant_tools`
- `jobs`
- `pains`
- `trust_concerns`
- `feature_implications`
- `messaging_implications`
- `example_urls`

Discovery target fields:

- `target_id`
- `platform`
- `kind`
- `name`
- `handle`
- `url`
- `priority`
- `rationale`
- `concept_fit`

Screening fields:

- `screen_stage`
- `concept_relevance_score`
- `concept_hits`
- `screen_reason`
