from fastapi import FastAPI

from api.routes.analysis import (
    router as analysis_router,
)

from api.routes.nutrition import (
    router as nutrition_router,
)


app = FastAPI(
    title="AI Gym",
    description="AI service for workout analysis",
    version="1.0.0",
)


app.include_router(
    analysis_router
)

app.include_router(
    nutrition_router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }