import os
from typing import Any

import httpx


USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"

USDA_API_KEY = os.getenv(
    "USDA_API_KEY",
    "DEMO_KEY",
)


class NutritionApiError(Exception):
    pass


async def search_food(
    food_name: str,
) -> dict[str, Any]:

    url = f"{USDA_API_URL}/foods/search"

    params = {
        "api_key": USDA_API_KEY,
        "query": food_name,
        "pageSize": 5,
    }

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

    if response.status_code != 200:
        raise NutritionApiError(
            f"USDA API error: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    foods = data.get("foods", [])

    if not foods:
        raise NutritionApiError(
            f"Food not found: {food_name}"
        )

    return foods[0]


async def get_food_details(
    fdc_id: int,
) -> dict[str, Any]:

    url = f"{USDA_API_URL}/food/{fdc_id}"

    params = {
        "api_key": USDA_API_KEY,
    }

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

    if response.status_code != 200:
        raise NutritionApiError(
            f"USDA API error: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()


def extract_nutrients(
    food: dict[str, Any],
) -> dict[str, float]:

    nutrients = food.get(
        "foodNutrients",
        [],
    )

    result = {
        "calories": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbohydrates": 0.0,
    }

    for nutrient in nutrients:

        name = nutrient.get(
            "nutrientName",
            "",
        ).lower()

        value = nutrient.get("value")

        if value is None:
            continue

        value = float(value)

        if (
            "energy" in name
            and "kcal" in name
        ):
            result["calories"] = value

        elif "protein" in name:
            result["protein"] = value

        elif (
            "total lipid" in name
            or name == "fat"
        ):
            result["fat"] = value

        elif "carbohydrate" in name:
            result["carbohydrates"] = value

    return result


async def find_food_nutrition(
    food_name: str,
) -> dict[str, Any]:

    search_result = await search_food(
        food_name
    )

    fdc_id = search_result.get("fdcId")

    if not fdc_id:
        raise NutritionApiError(
            f"FDC ID not found for: {food_name}"
        )

    food_details = await get_food_details(
        fdc_id
    )

    nutrients = extract_nutrients(
        food_details
    )

    return {
        "fdcId": fdc_id,
        "name": food_details.get(
            "description",
            food_name,
        ),
        "calories": nutrients["calories"],
        "protein": nutrients["protein"],
        "fat": nutrients["fat"],
        "carbohydrates": nutrients[
            "carbohydrates"
        ],
    }