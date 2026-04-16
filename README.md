# Gap Detection System

Graduation-project web system for detecting likely prerequisite gaps when a student returns to the Syrian curriculum after studying abroad.

The system does not judge one curriculum as better than another. It compares a student's actual studied path with the target Syrian curriculum path, then highlights prerequisite topics that may need teacher support.

## Current Structure

```text
frontend/
  index.html
  assets/
    app.js
    styles.css
  stitch_gap_detection_system/
    ...original Stitch exports and screenshots

backend/
  app/
    main.py
    logic/
    models/
    routes/
  Dockerfile
  requirements.txt

prototype/
  junior_curriculum_gap_prototype_v1.py

docs/
  api.md
  deployment.md
```

## Frontend

The frontend is a static GitHub Pages-ready demo shell. It preserves the visual direction of the Stitch prototype and wires the main teacher workflow to the backend endpoints.

The Knowledge Graph section uses Cytoscape.js in the browser to render interactive node-edge graphs from the backend's graph-ready JSON. It supports student-specific graphs and curriculum-slice graphs without requiring Neo4j infrastructure at this phase.

The Analytics link opens `frontend/analytics.html`, a standalone Arabic reference page for studies, statistics, and infographics that motivate the need for curriculum gap detection.

Open locally:

```powershell
Start-Process .\frontend\index.html
```

For GitHub Pages, configure Pages to publish from the `frontend/` folder if your repository settings allow it. If not, publish from a branch or copy the static frontend files into the Pages source branch during deployment.

## Backend

The backend uses FastAPI and refactors the original notebook-style logic into maintainable modules.

Run locally:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Health check:

```text
GET http://localhost:8080/health
```

## Data Source

By default, the backend reads the same Google Sheet used by the prototype:

- topics sheet
- prerequisite edges sheet
- student cases sheet

For Cloud Run or offline demos, set local CSV paths through environment variables:

```text
GAP_TOPICS_CSV=/app/data/topics.csv
GAP_PREREQ_CSV=/app/data/prerequisites.csv
GAP_STUDENT_CASES_CSV=/app/data/student_cases.csv
```

## Main API Routes

- `GET /health`
- `POST /analyze-student-case`
- `POST /student-graph`
- `POST /curriculum-graph`

## Deployment Direction

- Frontend: GitHub Pages static hosting.
- Backend: Cloud Run-ready Dockerfile in `backend/`.
- Graph layer: backend returns graph-ready `nodes` and `edges`; the current frontend renders them with Cytoscape.js, and Neo4j storage can be added later without changing the teacher workflow contract.
