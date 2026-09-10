import json
import re

from services.llm_client import generate


async def analyze_food_text(
    text: str,
) -> list[dict]:

    prompt = f"""
Ты анализируешь текст о съеденной пользователем еде.

Текст пользователя:
{text}

Определи все продукты питания, которые пользователь съел.

Для каждого продукта определи:
- название продукта на английском языке;
- количество продукта в граммах.

Если пользователь указал количество в штуках,
оцени примерный вес в граммах.

Не определяй калории.
Не определяй белки.
Не определяй жиры.
Не определяй углеводы.

Не добавляй продукты, которых нет в тексте.

Верни ТОЛЬКО JSON.

Формат:

{{
  "foods": [
    {{
      "name": "chicken breast",
      "weight": 200
    }}
  ]
}}

Если еды нет:

{{
  "foods": []
}}

Не используй Markdown.
Не добавляй пояснения.
"""

    response = await generate(
        prompt=prompt,
        temperature=0.1,
    )

    return _parse_response(response)


def _parse_response(
    response: str,
) -> list[dict]:

    response = response.strip()

    response = re.sub(
        r"```json\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"```\s*",
        "",
        response,
    )

    response = response.strip()

    try:
        data = json.loads(response)

    except json.JSONDecodeError as exception:
        raise ValueError(
            f"Gemma returned invalid JSON: {response}"
        ) from exception

    foods = data.get("foods")

    if not isinstance(foods, list):
        raise ValueError(
            "Gemma response does not contain foods list"
        )

    result = []

    for food in foods:

        if not isinstance(food, dict):
            continue

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

        result.append(
            {
                "name": str(name).strip(),
                "weight": weight,
            }
        )

    return result