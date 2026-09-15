# Climate & Pollination Dashboard Prototype

This repository contains two small applications that communicate over HTTP:

- **Frontend:** Next.js/React on `http://localhost:3000`
- **Backend:** FastAPI/Python on `http://localhost:8000`

Selecting a date in the sidebar sends this JSON request:

```http
POST /api/v1/inference
Content-Type: application/json

{"date":"2026-08-09"}
```

The placeholder Python model returns climate KPIs, pollination statistics, and
a small JSON raster grid. Replace the internals of
`model/placeholder_inference.py` with the real CNN and clustering pipeline later
while preserving its returned fields.

## First-time setup

From the repository root:

```powershell
npm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r model\requirements.txt
```

## Run the prototype

Open two PowerShell terminals in the repository root.

Terminal 1 — Python API:

```powershell
.\.venv\Scripts\Activate.ps1
npm run dev:backend
```

Terminal 2 — Next.js frontend:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). FastAPI's interactive API
documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Request path

```text
Date input
  -> DashboardContext.tsx
  -> lib/api.ts (HTTP POST + JSON)
  -> backend/main.py (FastAPI endpoint)
  -> model/placeholder_inference.py
  -> JSON response
  -> KPI cards, statistics, and map
```

## Environment setting

The frontend defaults to `http://localhost:8000`. To use a different API host,
set `NEXT_PUBLIC_API_BASE_URL` in a local `.env` file.
