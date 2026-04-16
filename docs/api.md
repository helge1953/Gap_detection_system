# API Contract

Base URL for local development:

```text
http://localhost:8080
```

## GET /health

Returns service status.

```json
{
  "status": "ok",
  "service": "gap-detection-backend"
}
```

## POST /analyze-student-case

Input:

```json
{
  "case_id": "SC_DEMO_001",
  "origin_country": "Turkey",
  "grades_studied_abroad": ["9", "10", "11"],
  "last_completed_grade_abroad": "11",
  "target_country": "Syria",
  "target_grade": "12",
  "target_stream": "Scientific",
  "subject_focus": "Math",
  "overall_difficulty": 6,
  "math_difficulty": 7,
  "notes": "Returning student preparing for Syrian scientific stream mathematics."
}
```

Output:

```json
{
  "summary": {},
  "teacher_alert_report": [],
  "support_first_topics": [],
  "graph_summary": {
    "nodes_count": 0,
    "edges_count": 0,
    "preview_nodes": [],
    "preview_edges": []
  }
}
```

## POST /student-graph

Uses the same student case input as `/analyze-student-case`.

Output:

```json
{
  "nodes": [],
  "edges": []
}
```

## POST /curriculum-graph

Input:

```json
{
  "country": "Syria",
  "grade": "12",
  "stream": "Scientific",
  "subject": "Math",
  "core_only": true
}
```

Output:

```json
{
  "nodes": [],
  "edges": []
}
```

## Graph Shape

Nodes use:

```json
{
  "id": "topic id",
  "label": "topic name",
  "group": "subject branch",
  "type": "target_topic | prereq_topic | curriculum_topic",
  "status": "target | likely_missed_due_to_switch | likely_covered_abroad | curriculum"
}
```

Edges use:

```json
{
  "source": "prerequisite topic id",
  "target": "target topic id",
  "type": "relation type",
  "strength": "required | helpful",
  "status": "coverage status when student-specific"
}
```

