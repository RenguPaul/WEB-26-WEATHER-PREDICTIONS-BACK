import builtins

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates

from data.collections import climate_predictions, climate_likes


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def published_predictions():
    """Возвращает только опубликованные прогнозы."""
    return [
        prediction
        for prediction in climate_predictions
        if prediction["status"] == "published"
    ]


def likes_count(prediction_id: int) -> int:
    """Рассчитывает количество лайков из отдельной коллекции."""
    return sum(
        1
        for like in climate_likes
        if like["prediction_id"] == prediction_id
    )


def add_like_counts(predictions):
    """Добавляет количество лайков к данным для шаблона."""
    result = []

    for prediction in predictions:
        item = dict(prediction)
        item["likes_count"] = likes_count(
            prediction["id"]
        )
        result.append(item)

    return result


@router.get("/forecast/{prediction_id}")
def get_prediction_feed(
    request: Request,
    prediction_id: int,
    next_page: bool = Query(
        default=False,
        alias="next",
    ),
):
    """
    Лента.

    GET по ID прогноза.
    Параметр ?next=true открывает следующий
    опубликованный прогноз.
    """

    predictions = published_predictions()

    current_index = builtins.next(
        (
            index
            for index, prediction in enumerate(predictions)
            if prediction["id"] == prediction_id
        ),
        None,
    )

    if current_index is None:
        raise HTTPException(
            status_code=404,
            detail="Прогноз не найден",
        )

    if next_page:
        next_index = current_index + 1

        if next_index >= len(predictions):
            next_index = 0

        prediction = predictions[next_index]

    else:
        prediction = predictions[current_index]

    context_prediction = dict(prediction)

    context_prediction["likes_count"] = likes_count(
        prediction["id"]
    )

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "prediction": context_prediction,
        },
    )


@router.get("/forecast/draft")
def get_draft_prediction(
    request: Request,
):
    """
    Страница добавления.

    Получает единственный черновой прогноз.
    """

    draft = next(
        (
            prediction
            for prediction in climate_predictions
            if prediction["status"] == "draft"
        ),
        None,
    )

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Черновик не найден",
        )

    context_prediction = dict(draft)

    context_prediction["likes_count"] = likes_count(
        draft["id"]
    )

    return templates.TemplateResponse(
        request=request,
        name="add.html",
        context={
            "prediction": context_prediction,
        },
    )


@router.get("/forecast/tile")
def get_prediction_tiles(
    request: Request,
    co2: float | None = Query(
        default=None,
        ge=0,
    ),
):
    """
    Плитка.

    Серверная фильтрация опубликованных прогнозов
    по числовому значению CO₂.
    """

    predictions = published_predictions()

    if co2 is not None:
        predictions = [
            prediction
            for prediction in predictions
            if prediction["co2_ppm"] == co2
        ]

    predictions = add_like_counts(
        predictions
    )

    return templates.TemplateResponse(
        request=request,
        name="tile.html",
        context={
            "predictions": predictions,
            "co2_filter": (
                ""
                if co2 is None
                else co2
            ),
        },
    )