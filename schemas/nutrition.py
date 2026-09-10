from datetime import date

from pydantic import BaseModel


class BodyProperties(BaseModel):
    birthDate: date
    weight: float
    height: float
    isMale: bool


class NutritionGoalRequest(BaseModel):
    userId: str
    bodyProperties: BodyProperties
    activityLevel: str
    goal: str
    targetWeight: float


class NutritionGoalResponse(BaseModel):
    currentWeight: float
    targetWeight: float

    bmi: float

    bmr: float
    tdee: float

    dailyCalories: float

    protein: float
    fat: float
    carbohydrates: float


# -------------------------
# Food
# -------------------------

class DetectedFood(BaseModel):
    name: str
    weight: float


class FoodNutrition(BaseModel):
    name: str
    weight: float
    calories: float
    protein: float
    fat: float
    carbohydrates: float


class NutritionTotal(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float


# -------------------------
# Image
# -------------------------

class AnalyzeFoodImageResponse(BaseModel):
    foods: list[FoodNutrition]
    total: NutritionTotal


# -------------------------
# Text
# -------------------------

class AnalyzeFoodTextRequest(BaseModel):
    text: str


class AnalyzeFoodTextResponse(BaseModel):
    foods: list[FoodNutrition]
    total: NutritionTotal