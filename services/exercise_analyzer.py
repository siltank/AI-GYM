from schemas.analysis import (
    AnalyzeExerciseRequest,
    AnalyzeExerciseResponse,
    ExerciseProgress,
    ExerciseRecommendation,
)

from services.llm_client import generate


WEIGHT_STEP = 2.5
PLATEAU_THRESHOLD = 3


def get_max_weight(workout) -> float | None:
    """
    Возвращает максимальный вес среди подходов тренировки.
    """

    if not workout.sets:
        return None

    return max(
        exercise_set.weight
        for exercise_set in workout.sets
    )


def get_working_weights(history) -> list[float]:
    """
    Возвращает максимальный рабочий вес
    каждой тренировки.
    """

    return [
        max_weight
        for workout in history
        if (max_weight := get_max_weight(workout)) is not None
    ]


def calculate_progress(
    history,
) -> ExerciseProgress:

    weights = get_working_weights(history)

    if not weights:
        return ExerciseProgress(
            weightChange=0.0,
            weightChangePercent=0.0,
            trend="NO_DATA",
        )

    initial_weight = weights[0]
    current_weight = weights[-1]

    weight_change = current_weight - initial_weight

    if initial_weight == 0:
        weight_change_percent = 0.0
    else:
        weight_change_percent = round(
            (weight_change / initial_weight) * 100,
            2,
        )

    if weight_change > 0:
        trend = "UP"
    elif weight_change < 0:
        trend = "DOWN"
    else:
        trend = "STABLE"

    return ExerciseProgress(
        weightChange=weight_change,
        weightChangePercent=weight_change_percent,
        trend=trend,
    )


def detect_plateau(
    history,
) -> tuple[bool, int]:

    weights = get_working_weights(history)

    if len(weights) < PLATEAU_THRESHOLD:
        return False, 0

    current_weight = weights[-1]

    workouts_without_progress = 0

    for weight in reversed(weights):

        if weight <= current_weight:
            workouts_without_progress += 1
        else:
            break

    if workouts_without_progress < PLATEAU_THRESHOLD:
        return False, 0

    start_index = len(history) - workouts_without_progress

    duration = (
        history[-1].datetime
        - history[start_index].datetime
    ).total_seconds()

    return True, int(duration)


def get_current_weight(history) -> float:
    """
    Возвращает текущий максимальный рабочий вес.
    """

    weights = get_working_weights(history)

    if not weights:
        return 0.0

    return weights[-1]


def make_recommendation(
    history,
    progress: ExerciseProgress,
    plateau_detected: bool,
) -> ExerciseRecommendation:

    current_weight = get_current_weight(history)

    # Если данных нет
    if current_weight == 0:
        return ExerciseRecommendation(
            action="NO_DATA",
            suggestedWeight=0.0,
        )

    # Если обнаружено плато
    if plateau_detected:
        return ExerciseRecommendation(
            action="BREAK_PLATEAU",
            suggestedWeight=current_weight,
        )

    # Если есть положительный прогресс
    if progress.trend == "UP":
        return ExerciseRecommendation(
            action="INCREASE_WEIGHT",
            suggestedWeight=current_weight + WEIGHT_STEP,
        )

    # Если вес снизился
    if progress.trend == "DOWN":
        return ExerciseRecommendation(
            action="MAINTAIN_WEIGHT",
            suggestedWeight=current_weight,
        )

    # Если прогресс отсутствует
    return ExerciseRecommendation(
        action="MAINTAIN_WEIGHT",
        suggestedWeight=current_weight,
    )


async def generate_ai_analysis(
    request: AnalyzeExerciseRequest,
    progress: ExerciseProgress,
    plateau_detected: bool,
    recommendation: ExerciseRecommendation,
) -> str:

    history_text = "\n".join(
        f"""
Дата: {workout.datetime.isoformat()}
Подходы:
{
    ", ".join(
        f"{exercise_set.weight} кг × {exercise_set.reps}"
        for exercise_set in workout.sets
    )
}
"""
        for workout in request.history
    )

    prompt = f"""
Ты AI-тренер приложения AI Gym.

Проанализируй тренировочный прогресс пользователя.

Упражнение:
{request.exercise.name}

Категория:
{request.exercise.category}

Мышечные группы:
{", ".join(request.exercise.muscleGroup)}

История тренировок:
{history_text}

Результаты математического анализа:

Начальный вес:
{progress.weightChange + get_current_weight(request.history) - progress.weightChange}

Текущий максимальный вес:
{get_current_weight(request.history)} кг

Изменение веса:
{progress.weightChange} кг

Изменение в процентах:
{progress.weightChangePercent}%

Тренд:
{progress.trend}

Плато:
{plateau_detected}

Рекомендованное действие:
{recommendation.action}

Рекомендуемый вес:
{recommendation.suggestedWeight} кг

ВАЖНО:

Не изменяй числовые результаты анализа.
Не придумывай собственные значения веса.
Не предлагай другой вес.

Твоя задача — только объяснить пользователю результаты анализа
простым и понятным языком.

Ответ должен содержать:

1. Краткую оценку прогресса.
2. Объяснение изменения нагрузки.
3. Информацию о наличии или отсутствии плато.
4. Краткое объяснение рекомендации.

Ответ на русском языке.
"""

    return await generate(prompt)


async def analyze_exercise(
    request: AnalyzeExerciseRequest,
) -> AnalyzeExerciseResponse:

    # Всегда анализируем историю в хронологическом порядке
    history = sorted(
        request.history,
        key=lambda workout: workout.datetime,
    )

    progress = calculate_progress(history)

    plateau_detected, plateau_duration = detect_plateau(
        history
    )

    recommendation = make_recommendation(
        history,
        progress,
        plateau_detected,
    )

    ai_analysis = await generate_ai_analysis(
        request,
        progress,
        plateau_detected,
        recommendation,
    )

    return AnalyzeExerciseResponse(
        exerciseId=request.exercise.id,
        progress=progress,
        plateauDetected=plateau_detected,
        plateauDurationSec=plateau_duration,
        recomendation=recommendation,
        aiAnalysis=ai_analysis,
    )