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

    # ДОБАВЬ СЮДА
    print("IMAGE SIZE:", len(image_bytes))
    print("CONTENT TYPE:", content_type)
    print("BASE64 SIZE:", len(image_base64))

    prompt = """
    Посмотри на фотографию.

    Назови ВСЕ продукты питания, которые видишь.

    Ответь ТОЛЬКО JSON:

    {
      "foods": [
        {
          "name": "chicken breast",
          "weight": 200
        }
      ]
    }

    Если не уверен в точном весе, укажи примерный вес.
    Не добавляй продукты, которых нет на фотографии.
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