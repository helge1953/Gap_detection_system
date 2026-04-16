"""Graph-ready output routes."""

from fastapi import APIRouter, HTTPException, status

from app.logic.analysis import build_curriculum_graph, build_student_graph
from app.logic.data_loader import DataLoadError
from app.models.student_case import CurriculumGraphInput, GraphResponse, StudentCaseInput

router = APIRouter(tags=["graphs"])


@router.post("/student-graph", response_model=GraphResponse)
def student_graph(case_input: StudentCaseInput) -> dict:
    try:
        return build_student_graph(case_input)
    except DataLoadError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/curriculum-graph", response_model=GraphResponse)
def curriculum_graph(input_data: CurriculumGraphInput) -> dict:
    try:
        return build_curriculum_graph(input_data)
    except DataLoadError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

