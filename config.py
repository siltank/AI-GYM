import os


LM_STUDIO_URL = os.getenv(
    "LM_STUDIO_URL",
    "http://host.docker.internal:2223",
)

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "google/gemma-3-4b",
)