import base64
import json
import re

from services.llm_client import generate


async def analyze_food_image(
    image_bytes: bytes,
    content_type: str,
) -> list[dict]:

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    print("IMAGE SIZE:", len(image_bytes))
    print("CONTENT TYPE:", content_type)
    print("BASE64 SIZE:", len(image_base64))

    prompt = """
Ты AI-тренер приложения AI Gym и анализируешь фотографию еды.

Внимательно посмотри на фотографию и определи продукты питания,
которые действительно видны на изображении.

Для каждого продукта определи:

1. Название продукта.
2. Примерный вес съеденной порции в граммах.
3. Примерное количество калорий.
4. Примерное количество белков в граммах.
5. Примерное количество жиров в граммах.
6. Примерное количество углеводов в граммах.

Правила анализа:

- Анализируй только то, что действительно видно на фотографии.
- Не придумывай продукты, которых нет на изображении.
- Не учитывай тарелки, стол, приборы, упаковку и другие несъедобные предметы.
- Если на фотографии несколько разных продуктов, укажи каждый отдельно.
- Если изображено готовое блюдо, постарайся определить его основные компоненты.
- Если невозможно точно определить продукт, используй наиболее общее корректное название.
- Вес порции является приблизительной визуальной оценкой.
- Калории и БЖУ также являются приблизительной оценкой.
- Не используй данные из предыдущих запросов.
- Не добавляй продукты только потому, что они обычно присутствуют
  в похожем блюде.
- Названия продуктов должны быть на английском языке.
- Не используй Markdown.
- Не добавляй пояснения до или после JSON.

Очень важно:

Калории, белки, жиры и углеводы должны соответствовать
указанному весу конкретной порции.

Например, если указано:

{
  "name": "chicken breast",
  "weight": 200
}

то calories, protein, fat и carbohydrates должны быть
для 200 граммов куриной грудки, а не для 100 граммов.

Верни только JSON следующего формата:

{
  "foods": [
    {
      "name": "chicken breast",
      "weight": 200,
      "calories": 330,
      "protein": 62,
      "fat": 7,
      "carbohydrates": 0
    }
  ]
}

Если на фотографии несколько продуктов:

{
  "foods": [
    {
      "name": "chicken breast",
      "weight": 200,
      "calories": 330,
      "protein": 62,
      "fat": 7,
      "carbohydrates": 0
    },
    {
      "name": "white rice",
      "weight": 150,
      "calories": 195,
      "protein": 4,
      "fat": 0.5,
      "carbohydrates": 42
    }
  ]
}

Если еды на фотографии нет:

{
  "foods": []
}
"""

    response = await generate(
        prompt=prompt,
        temperature=0.1,
        image_base64=image_base64,
        content_type=content_type,
    )

    print("GEMMA RESPONSE:", response)

    return _parse_response(response)


def _parse_response(
    response: str,
) -> list[dict]:

    response = response.strip()

    response = re.sub(
        r"```json",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"```",
        "",
        response,
    )

    response = response.strip()

    if not response.startswith("{"):

        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL,
        )

        if match:
            response = match.group(0)

    try:

        data = json.loads(response)

    except json.JSONDecodeError as exception:

        raise ValueError(
            "Gemma returned invalid JSON: "
            f"{response}"
        ) from exception

    foods = data.get("foods", [])

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
        calories = food.get("calories")
        protein = food.get("protein")
        fat = food.get("fat")
        carbohydrates = food.get("carbohydrates")

        if not name:
            continue

        if weight is None:
            continue

        if calories is None:
            continue

        if protein is None:
            continue

        if fat is None:
            continue

        if carbohydrates is None:
            continue

        try:

            weight = float(weight)
            calories = float(calories)
            protein = float(protein)
            fat = float(fat)
            carbohydrates = float(carbohydrates)

        except (
            TypeError,
            ValueError,
        ):
            continue

        if weight <= 0:
            continue

        if calories < 0:
            continue

        if protein < 0:
            continue

        if fat < 0:
            continue

        if carbohydrates < 0:
            continue

        result.append(
            {
                "name": str(name).strip(),
                "weight": weight,
                "calories": calories,
                "protein": protein,
                "fat": fat,
                "carbohydrates": carbohydrates,
            }
        )

    return result