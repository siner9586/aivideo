# Queue and Project System

AI Video Studio Beta adds a lightweight project system and asynchronous queue. Both are local-file based and do not require Redis or Celery.

## Queue storage

Task records are appended to:

```text
data/tasks/tasks.jsonl
```

Each task contains:

- `task_id`
- `project_id`
- `shot_id`
- `backend`
- `status`
- `progress`
- `input_prompt`
- `input_assets`
- `output_video_path`
- `error_message`
- `created_at`
- `updated_at`

Supported statuses:

- `pending`
- `running`
- `completed`
- `failed`
- `cancelled`

## Queue API

```http
POST /api/queue/submit
GET /api/queue/tasks
GET /api/queue/tasks/{task_id}
POST /api/queue/tasks/{task_id}/cancel
POST /api/queue/tasks/{task_id}/retry
```

The default worker starts with the FastAPI process. It runs selected backend generation and writes the result back to the matching project shot when `project_id` and `shot_id` are provided.

## Project storage

Project records are saved under:

```text
data/projects/{project_id}/project.json
data/projects/{project_id}/assets/
data/projects/{project_id}/outputs/
```

## Project API

```http
POST /api/projects
GET /api/projects
GET /api/projects/{project_id}
PUT /api/projects/{project_id}
DELETE /api/projects/{project_id}
POST /api/projects/{project_id}/shots
PUT /api/projects/{project_id}/shots/{shot_id}
DELETE /api/projects/{project_id}/shots/{shot_id}
POST /api/projects/{project_id}/save
POST /api/projects/{project_id}/export
```

## Extension path

This phase uses in-memory queue plus JSONL persistence. A later phase can replace the queue implementation with Redis, Celery or RQ while keeping the same API shape.
