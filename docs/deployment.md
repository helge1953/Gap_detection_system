# Deployment Notes

## Frontend on GitHub Pages

The frontend is static and lives in `frontend/`.

Recommended path:

1. Push the repository to GitHub.
2. In repository settings, enable GitHub Pages.
3. Publish the `frontend/` folder if available in the Pages UI.
4. If the UI only supports root or `/docs`, use a small deployment workflow later to publish `frontend/` to Pages.

The browser stores the backend URL in local storage. For local work, use:

```text
http://localhost:8080
```

For production, set it to the Cloud Run service URL.

## Backend on Cloud Run

The backend includes a Dockerfile:

```powershell
cd backend
docker build -t gap-detection-backend .
docker run -p 8080:8080 gap-detection-backend
```

Cloud Run should expose port `8080`.

## Data Strategy

The current backend can read directly from the Google Sheet used by the Python prototype. For a more controlled deployment, export the sheets as CSV files and provide them through environment variables:

```text
GAP_TOPICS_CSV=/app/data/topics.csv
GAP_PREREQ_CSV=/app/data/prerequisites.csv
GAP_STUDENT_CASES_CSV=/app/data/student_cases.csv
```

The `backend/data/` folder is reserved for local data files and ignored by Git by default.

## Future Neo4j Integration

The current graph endpoints return neutral `nodes` and `edges` arrays. The frontend renders those arrays directly with Cytoscape.js for a Neo4j-style exploration experience without requiring graph database infrastructure. A later Neo4j integration can:

1. Convert curriculum topics to `(:Topic)` nodes.
2. Convert prerequisite rows to `[:PREREQUISITE_OF]` relationships.
3. Store student-specific status as relationship or projection metadata.
4. Keep the frontend contract unchanged by still returning `nodes` and `edges`.
