"""Точка входа минимального API ЯОтель."""

from fastapi import FastAPI

app = FastAPI(
    title="ЯОтель API",
    version="0.1.0",
    description="Учебный API системы бронирования и управления гостиницей.",
)


@app.get("/health", tags=["health"], summary="Проверить доступность сервиса")
def health() -> dict[str, str]:
    """Возвращает минимальный ответ для health-check без раскрытия конфигурации."""
    return {"status": "ok"}
