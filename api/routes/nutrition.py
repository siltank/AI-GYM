from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.nutrition import (
    AnalyzeFoodImageResponse,
    FoodNutrition,
    NutritionTotal,
)
from services.food_image_analyzer import analyze_food_image
from services.food_nutrition import (
    calculate_food_nutrition,
    calculate_total_nutrition,
)


router = APIRouter(
    prefix="/internal/v1/nutrition",
    tags=["Nutrition"],
)


@router.post(
    "/analyze-image",
    response_model=AnalyzeFoodImageResponse,
)
async def analyze_food_image_endpoint(
    file: UploadFile = File(...),
):
    """
    Анализ фотографии еды.

    Gemma определяет продукты и примерный вес.
    USDA предоставляет пищевую ценность.
    Python рассчитывает КБЖУ для указанного веса.
    """

    # Проверяем, что файл действительно является изображением
    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Content-Type is missing",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image",
        )

    # Читаем изображение
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image is empty",
        )

    print(
        "RECEIVED IMAGE:",
        file.filename,
        file.content_type,
        len(image_bytes),
    )

    try:

        # ------------------------------------------------
        # 1. Gemma определяет продукты и их вес
        # ------------------------------------------------

        detected_foods = await analyze_food_image(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )

        print(
            "DETECTED FOODS:",
            detected_foods,
        )

        # Если Gemma не нашла еду
        if not detected_foods:

            return AnalyzeFoodImageResponse(
                foods=[],
                total=NutritionTotal(
                    calories=0,
                    protein=0,
                    fat=0,
                    carbohydrates=0,
                ),
            )

        # ------------------------------------------------
        # 2. USDA определяет пищевую ценность
        # ------------------------------------------------

        foods_with_nutrition = (
            await calculate_food_nutrition(
                detected_foods
            )
        )

        print(
            "FOODS WITH NUTRITION:",
            foods_with_nutrition,
        )

        # ------------------------------------------------
        # 3. Считаем общий КБЖУ фотографии
        # ------------------------------------------------

        total = calculate_total_nutrition(
            foods_with_nutrition
        )

        print(
            "TOTAL NUTRITION:",
            total,
        )

        # ------------------------------------------------
        # 4. Формируем response
        # ------------------------------------------------

        foods = [
            FoodNutrition(
                name=food["name"],
                weight=food["weight"],
                calories=food["calories"],
                protein=food["protein"],
                fat=food["fat"],
                carbohydrates=food["carbohydrates"],
            )
            for food in foods_with_nutrition
        ]

        return AnalyzeFoodImageResponse(
            foods=foods,
            total=NutritionTotal(
                calories=total["calories"],
                protein=total["protein"],
                fat=total["fat"],
                carbohydrates=total["carbohydrates"],
            ),
        )

    except Exception as exception:

        print(
            "NUTRITION ANALYSIS ERROR:",
            repr(exception),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to analyze food image",
        ) from exception