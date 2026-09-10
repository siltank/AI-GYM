from schemas.nutrition import (
    FoodNutrition,
    NutritionTotal,
)

from services.nutrition_api import (
    find_food_nutrition,
)


async def calculate_food_nutrition(
    foods: list[dict],
) -> tuple[
    list[FoodNutrition],
    NutritionTotal,
]:

    result = []

    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbohydrates = 0.0

    for food in foods:

        name = food["name"]
        weight = float(food["weight"])

        nutrition = await find_food_nutrition(
            name
        )

        multiplier = weight / 100.0

        calories = (
            nutrition["calories"]
            * multiplier
        )

        protein = (
            nutrition["protein"]
            * multiplier
        )

        fat = (
            nutrition["fat"]
            * multiplier
        )

        carbohydrates = (
            nutrition["carbohydrates"]
            * multiplier
        )

        food_nutrition = FoodNutrition(
            name=name,
            weight=weight,
            calories=round(
                calories,
                2,
            ),
            protein=round(
                protein,
                2,
            ),
            fat=round(
                fat,
                2,
            ),
            carbohydrates=round(
                carbohydrates,
                2,
            ),
        )

        result.append(food_nutrition)

        total_calories += calories
        total_protein += protein
        total_fat += fat
        total_carbohydrates += carbohydrates

    total = NutritionTotal(
        calories=round(
            total_calories,
            2,
        ),
        protein=round(
            total_protein,
            2,
        ),
        fat=round(
            total_fat,
            2,
        ),
        carbohydrates=round(
            total_carbohydrates,
            2,
        ),
    )

    return result, total