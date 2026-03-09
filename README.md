# PromptLab

PromptLab is a full-stack prompt engineering workspace for teams to create, organize, version, and manage prompt templates.

## Features

- FastAPI backend with typed Pydantic models
- Prompt CRUD with filter and search (`collection_id`, `search`)
- Collection CRUD with safe detachment of related prompts on delete
- Prompt version history with manual version creation and rollback
- React + Vite frontend with prompt and collection management flows
- Test suite with backend API coverage using `pytest`

## Tech Stack

- Backend: Python 3.11, FastAPI, Pydantic, Uvicorn
- Frontend: React 18, TypeScript, Vite
- Testing: Pytest, FastAPI TestClient
- Containerization: Docker, Docker Compose

## Repository Layout

```text
10x-engineer-project-repo/
|- backend/
|  |- app/
|  |  |- api.py
|  |  |- models.py
|  |  |- storage.py
|  |  `- utils.py
|  |- tests/
|  |- main.py
|  `- requirements.txt
|- frontend/
|  |- src/
|  |- package.json
|  `- vite.config.ts
|- docs/
|- specs/
|- PROJECT_BRIEF.md
|- GRADING_RUBRIC.md
`- docker-compose.yml
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Docker and Docker Compose (optional)

## Quick Start (Local)

### 1) Clone and enter the project

```bash
git clone <your-repo-url>
cd 10x-engineer-project-repo
```

### 2) Start backend

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
python main.py
```

Backend URLs:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### 3) Start frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

The frontend calls backend endpoints through `/api` using Vite's dev proxy.
To override the backend target during development:

```bash
VITE_DEV_PROXY_TARGET=http://localhost:8000 npm run dev
```

## Running Tests

From `backend/`:

```bash
source ../.venv/bin/activate
pytest -v
```

## Docker Compose

From the repository root:

```bash
docker-compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## API Summary

### Health

- `GET /health`

### Prompts

- `GET /prompts`
- `GET /prompts/{prompt_id}`
- `POST /prompts`
- `PUT /prompts/{prompt_id}`
- `PATCH /prompts/{prompt_id}`
- `DELETE /prompts/{prompt_id}`

### Prompt Versions

- `GET /prompts/{prompt_id}/versions`
- `GET /prompts/{prompt_id}/versions/{version_id}`
- `POST /prompts/{prompt_id}/versions`
- `POST /prompts/{prompt_id}/versions/{version_id}/rollback`

### Collections

- `GET /collections`
- `GET /collections/{collection_id}`
- `POST /collections`
- `PUT /collections/{collection_id}`
- `PATCH /collections/{collection_id}`
- `DELETE /collections/{collection_id}`

## Example API Calls

Create a collection:

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name":"Product Launch","description":"Launch-related prompts"}'
```

Create a prompt:

```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"title":"Blog Outline","content":"Create an outline for {{topic}}","description":"Outline prompt"}'
```

List prompts by search term:

```bash
curl "http://localhost:8000/prompts?search=blog"
```

## Development Notes

- Backend storage is currently in-memory and resets on restart.
- Validation errors are normalized to HTTP `400` responses.
- Use `pytest -v` before creating a pull request.

## Contributing

1. Create a feature branch.
2. Keep changes focused and well-tested.
3. Run backend tests: `cd backend && pytest -v`.
4. Open a pull request with a clear summary.

## Additional References

- Project assignment: `PROJECT_BRIEF.md`
- Grading criteria: `GRADING_RUBRIC.md`
- Feature specs: `specs/prompt-versions.md`, `specs/tagging-system.md`
