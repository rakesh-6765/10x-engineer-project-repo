# PromptLab Frontend

React + Vite frontend for PromptLab Week 4 deliverables.

## Scripts

```bash
npm install
npm run dev
npm run build
npm run lint
```

## Environment

The frontend uses `/api` by default and relies on the Vite dev proxy.
By default, `/api` is proxied to `http://localhost:8000`.

```bash
VITE_DEV_PROXY_TARGET=http://localhost:8000 npm run dev
```

If needed, you can still bypass the proxy by setting `VITE_API_BASE_URL` to a full backend URL.

## Structure

- `src/api/`: API client and resource modules
- `src/components/`: shared UI components
- `src/features/prompts/`: prompt list/form/filter modules
- `src/features/collections/`: collections management module
- `src/styles/`: global visual theme and responsive layout
