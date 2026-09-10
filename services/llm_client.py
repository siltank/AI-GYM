import os

import httpx


LM_STUDIO_URL = os.getenv(
    "LM_STUDIO_URL",
    "http://host.docker.internal:2223",
)

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "google/gemma-3-4b",
)


async def generate(
    prompt: str,
    temperature: float = 0.2,
    image_base64: str | None = None,
    content_type: str | None = None,
) -> str:

    url = f"{LM_STUDIO_URL}/v1/chat/completions"

    # =========================
    # IMAGE REQUEST
    # =========================

    if image_base64 is not None:

        if not content_type:
            content_type = "image/jpeg"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                +f"{image_base64}"
                            )
                        },
                    },
                ],
            }
        ]

    # =========================
    # TEXT REQUEST
    # =========================

    else:

        messages = [
            {
                "role": "system",
                "content": (
                    "Ты AI-тренер приложения AI Gym. "
                    "Анализируй данные пользователя "
                    "и давай краткие, понятные рекомендации. "
                    "Не выдумывай данные, которых нет "
                    "во входном запросе. "
                    "Python уже выполнил все математические "
                    "расчёты и определил рекомендацию. "
                    "Не изменяй числовые значения, "
                    "рассчитанные Python. "
                    "Не придумывай другой рекомендуемый вес. "
                    "Если передан suggestedWeight, "
                    "используй именно его. "
                    "Не используй Markdown."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
    }

    print("LLM URL:", url)
    print("LLM MODEL:", MODEL_NAME)
    print("HAS IMAGE:", image_base64 is not None)

    async with httpx.AsyncClient(
        timeout=120.0
    ) as client:

        response = await client.post(
            url,
            json=payload,
        )

    print("LLM STATUS:", response.status_code)

    if response.status_code != 200:
        print("LLM ERROR:", response.text)

        raise RuntimeError(
            f"LM Studio error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    choices = data.get("choices", [])

    if not choices:
        raise RuntimeError(
            "LM Studio returned no choices"
        )

    message = choices[0].get(
        "message",
        {},
    )

    content = message.get("content")

    if not content:
        raise RuntimeError(
            "LM Studio returned empty content"
        )

    print("LLM RESPONSE:", content)

    return content.strip()