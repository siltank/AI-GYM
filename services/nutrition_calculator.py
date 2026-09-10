from datetime import date



from schemas.nutrition import (
    NutritionGoalRequest,
    NutritionGoalResponse,
)


ACTIVITY_MULTIPLIERS = {
    "LOW": 1.2,
    "LIGHT": 1.375,
    "MODERATE": 1.55,
    "HIGH": 1.725,
    "VERY_HIGH": 1.9,
}


def calculate_age(birth_date: date) -> int:
    today = date.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (
        birth_date.month,
        birth_date.day,
    ):
        age -= 1

    return age


def calculate_bmi(
    weight: float,
    height: float,
) -> float:

    height_m = height / 100

    if height_m <= 0:
        return 0

    return round(
        weight / (height_m * height_m),
        2,
    )


def calculate_bmr(
    weight: float,
    height: float,
    age: int,
    sex: str,
) -> float:

    if sex.upper() == "MALE":
        return (
            10 * weight
            + 6.25 * height
            - 5 * age
            + 5
        )

    return (
        10 * weight
        + 6.25 * height
        - 5 * age
        - 161
    )


def calculate_tdee(
    bmr: float,
    activity_level: str,
) -> float:

    multiplier = ACTIVITY_MULTIPLIERS.get(
        activity_level.upper(),
        1.2,
    )

    return bmr * multiplier


def calculate_daily_calories(
    tdee: float,
    goal: str,
) -> float:

    goal = goal.upper()

    if goal == "LOSE_WEIGHT":
        return tdee - 500

    if goal == "GAIN_WEIGHT":
        return tdee + 300

    return tdee


def calculate_macros(
    calories: float,
    weight: float,
) -> tuple[float, float, float]:

    # Белок: 2 г / кг
    protein = weight * 2

    # Жиры: 1 г / кг
    fat = weight

    protein_calories = protein * 4
    fat_calories = fat * 9

    remaining_calories = (
        calories
        - protein_calories
        - fat_calories
    )

    carbohydrates = remaining_calories / 4

    return (
        round(protein, 1),
        round(fat, 1),
        round(max(carbohydrates, 0), 1),
    )


def calculate_nutrition_goal(
    request: NutritionGoalRequest,
) -> NutritionGoalResponse:

    body = request.bodyProperties

    age = calculate_age(
        body.birthDate,
    )

    bmi = calculate_bmi(
        body.weight,
        body.height,
    )

    bmr = calculate_bmr(
        weight=body.weight,
        height=body.height,
        age=age,
        sex="MALE" if request.bodyProperties.isMale else "FEMALE",
    )

    tdee = calculate_tdee(
        bmr=bmr,
        activity_level=request.activityLevel,
    )

    daily_calories = calculate_daily_calories(
        tdee=tdee,
        goal=request.goal,
    )

    protein, fat, carbohydrates = calculate_macros(
        calories=daily_calories,
        weight=body.weight,
    )

    return NutritionGoalResponse(
        currentWeight=body.weight,
        targetWeight=request.targetWeight,
        bmi=bmi,
        bmr=round(bmr, 1),
        tdee=round(tdee, 1),
        dailyCalories=round(daily_calories, 1),
        protein=protein,
        fat=fat,
        carbohydrates=carbohydrates,
    )