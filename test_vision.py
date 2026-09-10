import base64
import httpx


IMAGE_PATH = "C:/Users/Admin/Downloads/food.jpg"

with open(IMAGE_PATH, "rb") as file:
    image_base64 = base64.b64encode(
        file.read()
    ).decode("utf-8")


payload = {
    "model": "google/gemma-3-4b",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Посмотри на фотографию. "
                        "Назови все продукты питания, "
                        "которые ты видишь. "
                        "Ответь только списком продуктов."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            "data:image/jpeg;base64,"
                            + image_base64
                        )
                    },
                },
            ],
        },
    ],
    "temperature": 0.1,
}


response = httpx.post(
    "http://localhost:2223/v1/chat/completions",
    json=payload,
    timeout=120,
)

print("STATUS:", response.status_code)
print(response.text)