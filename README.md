## Update: Created the GitHub repository and published the full-stack architecture

The project now inclues

- a working front-end showcasing weather data
- a pipeline for image forecasts from the Machine Learning Model
- a HTTP connection via FastAPI between user input (forecasting date) and model output

## Outstanding

- Model training , fine tuning and feature engineering
- Database for cached forecasts

## Update (13rd August 2026): **Created the dashboard frontend prototype containing maps, statistics, and calendar view**

<img width="1433" height="792" alt="image" src="https://github.com/user-attachments/assets/4fbeb7e0-5d50-4933-a1b2-f4c806a95878" />


## Update(3rd Aug 2026): **Exported the satellite images using Google Eath Engine API and managed the outputs in Python and Google Drive.**

**Data checks and cleaning**

<img width="539" height="395" alt="image" src="https://github.com/user-attachments/assets/97569d9e-11ec-4a74-a7b4-a80e006898f3" />


<img width="527" height="403" alt="image" src="https://github.com/user-attachments/assets/58cf438d-fa77-4baf-bd61-09e9b83054f2" />


Investigated NDVI distribution for data checking

<img width="588" height="432" alt="image" src="https://github.com/user-attachments/assets/ed4eaf9c-cb10-4656-aa95-4ff0bee15c21" />


### Identified data quality issues due to cloud coverage

<img width="1790" height="590" alt="image" src="https://github.com/user-attachments/assets/d34bd211-a635-4338-b363-2da1faeb5b14" />


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
