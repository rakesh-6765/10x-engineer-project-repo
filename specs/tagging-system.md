# Tagging System Specification

## Purpose
Provide flexible tagging so teams can categorize prompts across collections and power search/filters.

## Goals
- Assign multiple tags to prompts without duplicating data.
- Filter prompts by one or many tags via API.
- Manage tag lifecycle (create, rename, delete) safely.

## User Stories
- As a prompt author, I can add tags to a prompt while creating or updating it.
- As a consumer, I can list prompts that match a set of tags.
- As an admin, I can rename or delete a tag without breaking existing prompts.

## Data Model
- `Tag`
  - `id` (string, UUID)
  - `name` (string, lowercase unique, 2-30 chars)
  - `created_at` (datetime, UTC)
- `PromptTag`
  - `prompt_id` (string, FK to Prompt)
  - `tag_id` (string, FK to Tag)
  - Composite uniqueness on (`prompt_id`, `tag_id`).

## API Endpoints
- `GET /tags` — list tags with optional `search` query.
- `POST /tags` — create a tag; rejects duplicates by `name` (case-insensitive).
- `PATCH /tags/{id}` — rename a tag.
- `DELETE /tags/{id}` — delete a tag and remove associations.
- `GET /prompts?tags=tag1,tag2` — filters prompts that include **all** requested tags; `match=any` query param can switch to OR behavior.
- Prompt creation/update payloads accept `tags: List[str]` of tag ids to attach.

## Behaviors & Rules
- Tag names stored lowercase; input normalized by trimming whitespace.
- Deleting a tag removes rows from `PromptTag` but does not delete prompts.
- When a prompt is updated, tag associations are replaced atomically with the provided list.
- Pagination mirrors existing list endpoints (`limit`, `offset`).

## Error Cases
- `400` for duplicate names, invalid tag ids, or bad `match` values.
- `404` when tag or prompt is missing.

## Acceptance Criteria
- Tags can be created, renamed, listed, and deleted through the API.
- Prompts can be filtered by tags with AND/OR semantics.
- Documentation includes payload examples and error responses.