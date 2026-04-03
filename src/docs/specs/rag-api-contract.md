# RAG API Contract

## Base path
`/digital-office/rag/`

## Endpoints

### 1) Create ingestion job
`POST /digital-office/rag/ingestions/`

#### Request fields
- `source_type`: `text | file | video`
- `tenant_id` (optional): fallback to `RAG_DEFAULT_TENANT_ID`
- `text_content` (for text)
- `file` (for file/video)
- `video_transcript` (required for video if transcript is not embedded in file pipeline)
- metadata fields:
  - `url`, `url_unique_id`, `source`, `format`, `id`, `uuid`,
  - `permission`, `department`, `division`, `user_id`, `group`
  - `metadata` (extra key-values)

#### Response
`202 Accepted`
- job status payload including `id`, `status`, `stage`, `progress_pct`, `celery_task_id`

### 2) Read ingestion job
`GET /digital-office/rag/ingestions/{job_id}/`

### 3) Query
`POST /digital-office/rag/query/`

#### Request
- `prompt` (required)
- `tenant_id` (optional)
- `top_k` (optional, clamped to `RAG_MAX_TOP_K`)
- `filters` (metadata filters)

#### Response
- `answer`
- `contexts[]`
- `references[]` (`vector_id`, `score`, `document_id`, `chunk_index`, `metadata`)
