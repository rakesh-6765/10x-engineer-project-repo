## Copilot Instructions

These notes guide AI assistants contributing to this repository.

### Coding Standards
- Prefer Python 3.10+ features; always include type hints on public functions.
- Follow Google-style docstrings with `Args`, `Returns`, and `Raises` when applicable.
- Keep functions small and side-effect aware; isolate I/O from business logic.
- Fail fast with clear HTTP errors in FastAPI routes; validate inputs before mutating state.
- Preserve compatibility with existing tests; avoid silent behavioral changes.

### Testing
- Add or update pytest cases when changing logic; arrange-act-assert and favor fixtures in `tests/conftest.py`.
- Run `pytest -v` for backend changes; include negative-path tests for error codes.

### Patterns That Work Well
- Pydantic models: use `Field` constraints and `default_factory` for IDs and timestamps.
- Storage layer: keep side effects in `Storage`; routes should be thin orchestration.
- Utilities: keep pure functions that accept data and return data without global state.
- API responses: wrap list responses in typed containers (e.g., `PromptList`) to keep schemas explicit.

### Style & Hygiene
- Stick to ASCII; keep line length readable (~100 chars).
- Avoid duplicating logic across routes and helpers; extract shared code into `utils.py` when needed.
- Document new endpoints in the README API reference and keep examples current.

### When In Doubt
- Ask for clarification on ambiguous requirements.
- Default to secure, predictable behavior; prefer explicit over implicit.