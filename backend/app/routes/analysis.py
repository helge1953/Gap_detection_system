"""Student analysis routes."""

from fastapi import APIRouter, HTTPException, status

from app.logic.analysis import analyze_student_case
from app.logic.data_loader import DataLoadError
from app.models.student_case import AnalysisResponse, StudentCaseInput

router = APIRouter(tags=["analysis"])


@router.post("/analyze-student-case", response_model=AnalysisResponse)
def analyze(case_input: StudentCaseInput) -> dict:
    try:
        return analyze_student_case(case_input)
    except DataLoadError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

