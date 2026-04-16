"""Request and response models for student case analysis."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StudentCaseInput(BaseModel):
    case_id: str | None = Field(default=None, examples=["SC_DEMO_001"])
    origin_country: str = Field(default="Turkey")
    grades_studied_abroad: list[str] | str = Field(default_factory=lambda: ["9", "10", "11"])
    last_completed_grade_abroad: str | None = Field(default="11")
    target_country: str = Field(default="Syria")
    target_grade: str = Field(default="12")
    target_stream: str | None = Field(default="Scientific")
    subject_focus: str = Field(default="Math")
    overall_difficulty: float | None = Field(default=None, ge=0, le=10)
    math_difficulty: float | None = Field(default=None, ge=0, le=10)
    notes: str | None = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)


class CurriculumGraphInput(BaseModel):
    country: str = "Syria"
    grade: str = "12"
    stream: str | None = "Scientific"
    subject: str = "Math"
    core_only: bool = True


class AnalysisResponse(BaseModel):
    summary: dict[str, Any]
    teacher_alert_report: list[dict[str, Any]]
    support_first_topics: list[dict[str, Any]]
    graph_summary: dict[str, Any]


class GraphResponse(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]

