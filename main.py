from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.handlers import router


app = FastAPI(
    title="Climate Temperature Forecast",
    description=(
        "Учебное приложение для прогнозирования изменения "
        "глобальной средней температуры Земли "
        "в зависимости от концентрации парниковых газов."
    ),
)

# Подключаем папку со стилями.
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

# Подключаем маршруты приложения.
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )