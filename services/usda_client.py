import os
from typing import Any

import httpx


USDA_API_KEY = os.getenv("USDA_API_KEY")

USDA_BASE_URL = (
    "https://api.nal.usda.gov/fdc/v1"
)


class USDAClient:

    def __init__(
        self,
        api_key: str | None = None,
    ):
        self.api_key = (
            api_key
            or USDA_API_KEY
        )

        if not self.api_key:
            raise RuntimeError(
                "USDA_API_KEY is not configured"
            )

    async def search_food(
        self,
        food_name: str,
    ) -> dict[str, Any] | None:

        url = (
            f"{USDA_BASE_URL}/foods/search"
        )

        params = {
            "api_key": self.api_key,
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
            raise RuntimeError(
                "USDA API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        foods = data.get(
            "foods",
            [],
        )

        if not foods:
            return None

        # Берём первый найденный продукт
        return foods[0]

    async def get_food_nutrition(
        self,
        food_name: str,
    ) -> dict[str, float] | None:

        food = await self.search_food(
            food_name
        )

        if not food:
            return None

        nutrients = food.get(
            "foodNutrients",
            []
        )

        calories = 0.0
        protein = 0.0
        fat = 0.0
        carbohydrates = 0.0

        for nutrient in nutrients:

            nutrient_name = (
                nutrient.get("nutrientName", "")
                .lower()
            )

            value = nutrient.get(
                "value",
                0,
            )

            if "energy" in nutrient_name:
                unit = nutrient.get(
                    "unitName",
                    ""
                )

                if unit.upper() == "KCAL":
                    calories = float(value)

            elif nutrient_name == "protein":
                protein = float(value)

            elif (
                "total lipid" in nutrient_name
                or nutrient_name == "fat"
            ):
                fat = float(value)

            elif (
                "carbohydrate" in nutrient_name
            ):
                carbohydrates = float(value)

        return {
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbohydrates": carbohydrates,
        }


usda_client = USDAClient()