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

    system_content = (
        "Ты AI-тренер приложения AI Gym. "
        "Анализируй данные пользователя. "
        "Не выдумывай данные, которых нет во входном запросе. "
        "Отвечай кратко и понятно. "
        "Не используй Markdown, символы **, *, #, _, ``` "
        "или другие элементы форматирования."
    )

    if image_base64 is not None:

        user_content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        f"data:{content_type};"
                        f"base64,{image_base64}"
                    )
                },
            },
        ]

    else:

        user_content = prompt

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "temperature": temperature,
    }

    async with httpx.AsyncClient(
        timeout=120.0
    ) as client:

        response = await client.post(
            url,
            json=payload,
        )

    if response.status_code != 200:
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

    message = choices[0].get("message", {})

    content = message.get("content")

    if not content:
        raise RuntimeError(
            "LM Studio returned empty content"
        )

    return content.strip()