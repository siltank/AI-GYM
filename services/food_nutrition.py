from services.usda_client import usda_client


async def calculate_food_nutrition(
    foods: list[dict],
) -> list[dict]:

    result = []

    for food in foods:

        name = food.get("name")
        weight = food.get("weight")

        if not name or weight is None:
            continue

        try:
            weight = float(weight)
        except (TypeError, ValueError):
            continue

        if weight <= 0:
            continue

        # Ищем продукт в USDA
        nutrition = await usda_client.get_food_nutrition(
            name
        )

        if nutrition is None:
            print(
                f"USDA FOOD NOT FOUND: {name}"
            )
            continue

        # USDA предоставляет значения на 100 г.
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

        result.append(
            {
                "name": name,
                "weight": round(weight, 1),
                "calories": round(
                    calories,
                    1,
                ),
                "protein": round(
                    protein,
                    1,
                ),
                "fat": round(
                    fat,
                    1,
                ),
                "carbohydrates": round(
                    carbohydrates,
                    1,
                ),
            }
        )

    return result


def calculate_total_nutrition(
    foods: list[dict],
) -> dict:

    calories = 0.0
    protein = 0.0
    fat = 0.0
    carbohydrates = 0.0

    for food in foods:

        calories += float(
            food.get("calories", 0)
        )

        protein += float(
            food.get("protein", 0)
        )

        fat += float(
            food.get("fat", 0)
        )

        carbohydrates += float(
            food.get("carbohydrates", 0)
        )

    return {
        "calories": round(
            calories,
            1,
        ),
        "protein": round(
            protein,
            1,
        ),
        "fat": round(
            fat,
            1,
        ),
        "carbohydrates": round(
            carbohydrates,
            1,
        ),
    }