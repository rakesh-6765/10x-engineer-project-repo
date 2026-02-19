# Prompt Versions Specification

## Purpose
Track immutable versions of prompts so teams can audit history, compare changes, and roll back safely.

## Goals
- Preserve every prompt edit with metadata (author, timestamp, change summary).
- Allow consumers to fetch the latest or a specific version.
- Enable rollbacks that create a new version referencing the origin version.

## User Stories
- As a prompt author, I can see a timeline of changes for any prompt.
- As a reviewer, I can fetch a specific version and diff it against another.
- As an operator, I can roll back a prompt to a prior version without losing newer history.

## Data Model
- `PromptVersion`
  - `id` (string, UUID)
  - `prompt_id` (string, FK to Prompt)
  - `title` (string)
  - `content` (string)
  - `description` (string, optional)
  - `collection_id` (string, optional)
  - `created_at` (datetime, UTC)
  - `author` (string, optional; defaults to "system" when unavailable)
  - `change_note` (string, optional; short free text)
  - `source_version_id` (string, optional; reference for rollbacks or clones)

## API Endpoints
- `GET /prompts/{id}/versions` — list versions (query: `limit`, `offset`), returns `{ versions: [...], total }` sorted newest first.
- `GET /prompts/{id}/versions/{version_id}` — fetch a specific version.
- `POST /prompts/{id}/versions` — create a new version manually; body mirrors prompt fields plus optional `change_note` and `author`.
- `POST /prompts/{id}/versions/{version_id}/rollback` — creates a new version that copies the target version and sets `source_version_id` to the target; also updates the live prompt.

## Behaviors & Rules
- Every PUT/PATCH to `/prompts/{id}` should create a `PromptVersion` snapshot before applying changes.
- Rollback does **not** delete versions; it appends a new version referencing `source_version_id`.
- Version lists default to 20 items with pagination support.
- Validation: `change_note` max 280 chars; reject empty `title` or `content` as per Prompt rules.

## Error Cases
- `404` when prompt or version is missing.
- `400` when rollback target belongs to a different prompt or payload fails validation.

## Acceptance Criteria
- Versions are created on every update path and visible via list endpoint.
- Rollback produces a new version and updates the prompt content atomically.
- API reference updated with request/response examples and error codes.