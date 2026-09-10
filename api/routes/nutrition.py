from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from schemas.nutrition import (
    AnalyzeFoodImageResponse,
    AnalyzeFoodTextRequest,
    AnalyzeFoodTextResponse,
    NutritionGoalRequest,
    NutritionGoalResponse,
)

from services.food_image_analyzer import (
    analyze_food_image,
)

from services.food_nutrition import (
    calculate_food_nutrition,
)

from services.food_text_analyzer import (
    analyze_food_text,
)

from services.nutrition_calculator import (
    calculate_nutrition_goal,
)


router = APIRouter(
    prefix="/internal/v1/nutrition",
    tags=["Nutrition"],
)


@router.post(
    "/goal",
    response_model=NutritionGoalResponse,
)
def calculate_goal(
    request: NutritionGoalRequest,
) -> NutritionGoalResponse:

    return calculate_nutrition_goal(request)


@router.post(
    "/analyze-text",
    response_model=AnalyzeFoodTextResponse,
)
async def analyze_food_text_endpoint(
    request: AnalyzeFoodTextRequest,
) -> AnalyzeFoodTextResponse:

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty",
        )

    try:

        foods = await analyze_food_text(
            request.text
        )

        if not foods:
            raise HTTPException(
                status_code=400,
                detail="No food products detected",
            )

        nutrition, total = (
            await calculate_food_nutrition(
                foods
            )
        )

        return AnalyzeFoodTextResponse(
            foods=nutrition,
            total=total,
        )

    except HTTPException:
        raise

    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Food analysis failed: "
                f"{exception}"
            ),
        )


@router.post(
    "/analyze-image",
    response_model=AnalyzeFoodImageResponse,
)
async def analyze_food_image_endpoint(
    image: UploadFile = File(...),
) -> AnalyzeFoodImageResponse:

    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Image content type is required",
        )

    if not image.content_type.startswith(
        "image/"
    ):
        raise HTTPException(
            status_code=401,
            detail="Uploaded file must be an image",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=402,
            detail="Uploaded image is empty",
        )

    try:

        foods = await analyze_food_image(
            image_bytes=image_bytes,
            content_type=image.content_type,
        )

        if not foods:
            raise HTTPException(
                status_code=403,
                detail="No food products detected",
            )

        nutrition, total = (
            await calculate_food_nutrition(
                foods
            )
        )

        return AnalyzeFoodImageResponse(
            foods=nutrition,
            total=total,
        )

    except HTTPException:
        raise

    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Food analysis failed: "
                f"{exception}"
            ),
        )