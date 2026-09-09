from datetime import datetime

from pydantic import BaseModel


class Equipment(BaseModel):
    id: str
    name: str
    description: str


class Exercise(BaseModel):
    id: str
    name: str
    description: str
    category: str
    muscleGroup: list[str]
    equipment: Equipment | None = None


class ExerciseSet(BaseModel):
    weight: float
    reps: int


class ExerciseHistory(BaseModel):
    datetime: datetime
    sets: list[ExerciseSet]


class AnalyzeExerciseRequest(BaseModel):
    userId: str
    exercise: Exercise
    history: list[ExerciseHistory]


class ExerciseProgress(BaseModel):
    weightChange: float
    weightChangePercent: float
    trend: str


class ExerciseRecommendation(BaseModel):
    action: str
    suggestedWeight: float


class AnalyzeExerciseResponse(BaseModel):
    exerciseId: str
    progress: ExerciseProgress
    plateauDetected: bool
    plateauDurationSec: int
    recomendation: ExerciseRecommendation
    aiAnalysis: str