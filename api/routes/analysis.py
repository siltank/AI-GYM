from fastapi import APIRouter

from schemas.analysis import (
    AnalyzeExerciseRequest,
    AnalyzeExerciseResponse,
)

from services.exercise_analyzer import analyze_exercise


router = APIRouter(
    prefix="/internal/v1/analyze",
    tags=["Analysis"],
)


@router.post(
    "/exercise",
    response_model=AnalyzeExerciseResponse,
)
async def analyze_exercise_endpoint(
    request: AnalyzeExerciseRequest,
) -> AnalyzeExerciseResponse:

    return await analyze_exercise(request)