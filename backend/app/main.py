from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import (
    auth_controller,
    dashboard_controller,
    gamification_controller,
    goal_controller,
    habit_controller,
    report_controller,
    task_controller,
    telegram_controller,
    user_controller,
)
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, prefix="/api")
app.include_router(user_controller.router, prefix="/api")
app.include_router(task_controller.router, prefix="/api")
app.include_router(habit_controller.router, prefix="/api")
app.include_router(dashboard_controller.router, prefix="/api")
app.include_router(telegram_controller.router, prefix="/api")
app.include_router(goal_controller.router, prefix="/api")
app.include_router(gamification_controller.router, prefix="/api")
app.include_router(report_controller.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
