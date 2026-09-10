import math

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.collections import greenhouse_gases


router = APIRouter()

templates = Jinja2Templates(directory="templates")

MINIO_URL = "http://localhost:9000/climate-media"

REFERENCE_CO2_PPM = 280.0
CLIMATE_SENSITIVITY_C = 3.0


def get_published_greenhouse_gases():
    """
    Возвращает только опубликованные услуги.

    Услуги со статусами draft и deleted
    в интерфейсе не отображаются.
    """
    return [
        greenhouse_gas
        for greenhouse_gas in greenhouse_gases
        if greenhouse_gas["status"] == "published"
    ]


def calculate_temperature_change(concentration_ppm: float):
    """
    Упрощённый расчёт изменения средней температуры
    для CO2 относительно базовой концентрации 280 ppm.

    Формула:

        ΔT = S * log2(C / C0)

    где:

        S  = 3 °C
        C0 = 280 ppm
        C  = указанная концентрация CO2
    """

    if concentration_ppm <= 0:
        return 0.0

    return round(
        CLIMATE_SENSITIVITY_C
        * math.log2(
            concentration_ppm / REFERENCE_CO2_PPM
        ),
        1,
    )


def prepare_greenhouse_gas(greenhouse_gas):
    """
    Подготавливает данные услуги для HTML-шаблона.

    Температура здесь НЕ рассчитывается,
    потому что она является результатом расчёта
    на странице заявки.
    """

    prepared = greenhouse_gas.copy()

    # Количество лайков вычисляется из массива ID пользователей.
    prepared["likes_count"] = len(
        greenhouse_gas["likes"]
    )

    # Ссылки на медиафайлы MinIO.
    prepared["image_url"] = (
        f"{MINIO_URL}/{greenhouse_gas['image_key']}"
    )

    prepared["video_url"] = (
        f"{MINIO_URL}/{greenhouse_gas['video_key']}"
    )

    return prepared


# ============================================================
# 1. СТРАНИЦА ЗАЯВКИ
# ============================================================

@router.get(
    "/greenhouse-gases/request",
    response_class=HTMLResponse,
)
def get_greenhouse_gas_request(request: Request):
    """
    Получение единственной услуги со статусом draft.

    Новые услуги не создаются и не сохраняются.
    """

    draft = next(
        (
            greenhouse_gas
            for greenhouse_gas in greenhouse_gases
            if greenhouse_gas["status"] == "draft"
        ),
        None,
    )

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Черновик парникового газа не найден",
        )

    greenhouse_gas = prepare_greenhouse_gas(draft)

    # Расчёт показывается только на странице заявки.
    if draft["formula"] == "CO2":
        greenhouse_gas["temperature_change"] = (
            calculate_temperature_change(
                draft["concentration_ppm"]
            )
        )
    else:
        greenhouse_gas["temperature_change"] = None

    return templates.TemplateResponse(
        request=request,
        name="greenhouse_gas_request.html",
        context={
            "request": request,
            "greenhouse_gas": greenhouse_gas,
        },
    )


# ============================================================
# 2. КАТАЛОГ
# ============================================================

@router.get(
    "/greenhouse-gases/catalog",
    response_class=HTMLResponse,
)
def get_greenhouse_gas_catalog(
    request: Request,
    concentration: float | None = Query(
        default=None
    ),
):
    """
    Список опубликованных услуг.

    Фильтрация выполняется на сервере
    по концентрации парникового газа.
    """

    published = get_published_greenhouse_gases()

    if concentration is not None:
        published = [
            greenhouse_gas
            for greenhouse_gas in published
            if greenhouse_gas["concentration_ppm"]
            <= concentration
        ]

    prepared = [
        prepare_greenhouse_gas(greenhouse_gas)
        for greenhouse_gas in published
    ]

    return templates.TemplateResponse(
        request=request,
        name="greenhouse_gas_catalog.html",
        context={
            "request": request,
            "greenhouse_gases": prepared,

            # Значение фильтра сохраняется после GET-запроса.
            "concentration_filter": (
                concentration
                if concentration is not None
                else 600
            ),

            "filter_applied": (
                concentration is not None
            ),
        },
    )


# ============================================================
# 3. ЛЕНТА
# ============================================================

@router.get(
    "/greenhouse-gases/{greenhouse_gas_id}",
    response_class=HTMLResponse,
)
def get_greenhouse_gas(
    request: Request,
    greenhouse_gas_id: int,
    go_next: bool = Query(
        default=False,
        alias="next",
    ),
):
    """
    Страница услуги в формате вертикальной ленты.

    /greenhouse-gases/1
        открывает услугу с ID 1.

    /greenhouse-gases/1?next=true
        открывает следующую опубликованную услугу.
    """

    published = get_published_greenhouse_gases()

    current_index = next(
        (
            index
            for index, greenhouse_gas
            in enumerate(published)
            if greenhouse_gas["id"]
            == greenhouse_gas_id
        ),
        None,
    )

    if current_index is None:
        raise HTTPException(
            status_code=404,
            detail="Парниковый газ не найден",
        )

    # Переход к следующей опубликованной услуге.
    if go_next:

        next_index = current_index + 1

        # После последней услуги возвращаемся
        # к первой опубликованной.
        if next_index >= len(published):
            next_index = 0

        greenhouse_gas = published[next_index]

    else:
        greenhouse_gas = published[current_index]

    prepared = prepare_greenhouse_gas(
        greenhouse_gas
    )

    return templates.TemplateResponse(
        request=request,
        name="greenhouse_gas.html",
        context={
            "request": request,
            "greenhouse_gas": prepared,
        },
    )