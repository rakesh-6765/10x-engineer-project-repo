# PromptLab

**Your AI Prompt Engineering Platform**
# Clone the repo
```
# PromptLab

AI prompt engineering workspace for teams to store, version, tag, and test prompt templates.

---

## Overview

PromptLab lets AI engineers collaborate on prompt assets with structure and auditability. Key capabilities include organized collections, tagging and search, basic version history, and an API you can wire into your own tooling. The backend ships with FastAPI and Pydantic; the frontend and CI/CD arrive in later phases.

---

## Quick Start

1. Install prerequisites: Python 3.10+, pip, Git (Node.js 18+ for later frontend work).
2. Clone and enter the repository:
	 ```bash
	 git clone <your-repo-url>
	 cd 10x-engineer-project-repo/backend
	 ```
3. Create a virtual environment (recommended) and install backend dependencies:
	 ```bash
	 python3 -m venv .venv
	 source .venv/bin/activate
	 pip install -r requirements.txt
	 ```
4. Run the API locally:
	 ```bash
	 python main.py
	 ```
	 - Base URL: http://localhost:8000
	 - Interactive docs: http://localhost:8000/docs
5. Run tests:
	 ```bash
	 pytest tests/ -v
	 ```

---

## Project Structure

```
10x-engineer-project-repo/
├── README.md
├── PROJECT_BRIEF.md
├── GRADING_RUBRIC.md
├── backend/
│   ├── app/
│   │   ├── api.py          # FastAPI routes
│   │   ├── models.py       # Pydantic schemas
│   │   ├── storage.py      # In-memory persistence layer
│   │   └── utils.py        # Helpers
│   ├── tests/
│   └── main.py             # Entry point
├── specs/
└── docs/
```

---

## API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health and version |
| GET | `/prompts` | List prompts (filter by collection or search) |
| GET | `/prompts/{id}` | Retrieve a single prompt |
| POST | `/prompts` | Create a prompt |
| PUT | `/prompts/{id}` | Replace a prompt |
| PATCH | `/prompts/{id}` | Partially update a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |
| GET | `/collections` | List collections |
| GET | `/collections/{id}` | Retrieve a collection |
| POST | `/collections` | Create a collection |
| DELETE | `/collections/{id}` | Delete a collection and detach prompts |

---

## Usage Examples

- Create a collection
	```bash
	curl -X POST http://localhost:8000/collections \
		-H "Content-Type: application/json" \
		-d '{"name":"Product Launch","description":"Prompts for launch assets"}'
	```

- Create a prompt in that collection
	```bash
	curl -X POST http://localhost:8000/prompts \
		-H "Content-Type: application/json" \
		-d '{"title":"Blog Outline","content":"Create an outline for {{topic}}","description":"Short blog outline","collection_id":"<collection-id>"}'
	```

- List prompts, filtered by collection and search term
	```bash
	curl "http://localhost:8000/prompts?collection_id=<collection-id>&search=blog"
	```

- Update a prompt
	```bash
	curl -X PUT http://localhost:8000/prompts/<prompt-id> \
		-H "Content-Type: application/json" \
		-d '{"title":"Blog Outline v2","content":"Draft a detailed outline for {{topic}}","description":"More detailed"}'
	```

---

## API Reference

### Health
- **GET /health**
	- Response: `200 OK`
		```json
		{"status": "healthy", "version": "0.1.0"}
		```

### Prompts
- **GET /prompts** — Query params: `collection_id`, `search`
	- Response: `200 OK`
		```json
		{"prompts": [...], "total": 2}
		```

- **GET /prompts/{id}**
	- Response: `200 OK` with a single prompt.

- **POST /prompts**
	- Request body:
		```json
		{"title": "Welcome DM", "content": "Greet {{name}}", "description": "Welcome message", "collection_id": "<collection-id>"}
		```
	- Response: `201 Created` with stored prompt including `id`, `created_at`, `updated_at`.

- **PUT /prompts/{id}**
	- Use to replace all prompt fields; preserves `id` and `created_at`.

- **PATCH /prompts/{id}**
	- Use to update only provided fields; omitting a field leaves it unchanged.

- **DELETE /prompts/{id}**
	- Response: `204 No Content` when deleted.

### Collections
- **GET /collections** — Returns `{ "collections": [...], "total": n }`.
- **GET /collections/{id}** — Returns a single collection.
- **POST /collections** — Creates and returns the new collection.
- **DELETE /collections/{id}** — Deletes the collection and nulls `collection_id` on related prompts.

### Errors
- Errors are returned as JSON with an HTTP status code and message, for example:
	```json
	{"detail": "Prompt not found"}
	```
- Common codes: `400 Bad Request` (invalid collection reference), `404 Not Found` (missing prompt or collection).

---

## Need Help?

- Read `PROJECT_BRIEF.md` for the assignment narrative.
- Check `GRADING_RUBRIC.md` to understand expectations.
- Use `pytest` to validate changes before opening PRs.
3. Check `GRADING_RUBRIC.md` to understand expectations
4. Ask questions in the course forum

---

Good luck, and welcome to the team! 🚀
