from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from data.collections import climate_predictions


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_published_predictions():
    return [
        prediction
        for prediction in climate_predictions
        if prediction["status"] == "published"
    ]


def prepare_prediction(prediction):
    prepared_prediction = prediction.copy()
    prepared_prediction["likes_count"] = len(prediction["likes"])
    return prepared_prediction


@router.get("/forecast/draft", response_class=HTMLResponse)
async def get_draft(request: Request):
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

    return templates.TemplateResponse(
        request=request,
        name="add.html",
        context={
            "prediction": prepare_prediction(draft),
        },
    )


@router.get("/forecast/tile", response_class=HTMLResponse)
async def get_tile(
    request: Request,
    co2: int | None = Query(default=None),
):
    predictions = get_published_predictions()

    if co2 is not None:
        predictions = [
            prediction
            for prediction in predictions
            if prediction["co2_ppm"] == co2
        ]

    predictions = [
        prepare_prediction(prediction)
        for prediction in predictions
    ]

    return templates.TemplateResponse(
        request=request,
        name="tile.html",
        context={
            "request": request,
            "predictions": predictions,
            "co2_filter": co2 if co2 is not None else "",
        },
    )


@router.get("/forecast/{prediction_id}", response_class=HTMLResponse)
async def get_forecast(
    request: Request,
    prediction_id: int,
    next: bool = Query(default=False),
):
    published = get_published_predictions()

    current_index = next(
        (
            index
            for index, prediction in enumerate(published)
            if prediction["id"] == prediction_id
        ),
        None,
    )

    if current_index is None:
        raise HTTPException(
            status_code=404,
            detail="Прогноз не найден",
        )

    if next:
        next_index = current_index + 1

        if next_index >= len(published):
            next_index = 0

        prediction = published[next_index]
    else:
        prediction = published[current_index]

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "request": request,
            "prediction": prepare_prediction(prediction),
        },
    )