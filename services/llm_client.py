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
) -> str:

    url = f"{LM_STUDIO_URL}/v1/chat/completions"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты AI-тренер приложения AI Gym. "
                    "Анализируй тренировочные данные пользователя "
                    "и давай краткие, понятные рекомендации. "
                    "Не выдумывай данные, которых нет во входном запросе."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]