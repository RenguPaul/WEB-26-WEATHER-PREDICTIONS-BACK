# Climate Forecast Backend

Лабораторная работа №1 на FastAPI и Jinja2.

* Тема: «Прогноз температуры на Земле в зависимости от содержания парниковых газов в атмосфере. Услуги - парниковые газы (углекисный газ, метан, оксид азота и тд), заявка - расчет средней температуры по указанной концентраци (в ppm) парниковых газов».
* Карточка: `climate_prediction` — климатический прогноз.
* Поля: `co2_ppm`, `ch4_ppb`, `n2o_ppb` и `temperature_change_c`.
* Прогноз содержит изображение, видео, описание и количество лайков.
* Данные хранятся в Python-коллекции.
* Медиафайлы хранятся в MinIO.
* Дизайн-референс: [UCAR SciEd](https://scied.ucar.edu/interactive).

## Запуск

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
docker compose up -d
python main.py
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python main.py
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:8000
```

MinIO Console:

```text
http://127.0.0.1:9001
```

MinIO API:

```text
http://127.0.0.1:9000
```

## MinIO

Для хранения изображений и видео используется MinIO.

Bucket:

```text
climate-media
```

В данных прогнозов хранятся ключи файлов:

```text
image_key
video_key
```

URL медиафайлов формируются на стороне FastAPI:

```text
http://localhost:9000/climate-media/<file>
```

Например:

```text
http://localhost:9000/climate-media/co2-double.jpg
```

Для доступа к MinIO Console используются данные из `docker-compose.yml`:

```text
Login: root
Password: rootpassword
```

## Три GET-маршрута

* `GET /forecast/tile` — каталог опубликованных прогнозов и фильтрация по концентрации CO₂.
* `GET /forecast/draft` — страница добавления нового прогноза.
* `GET /forecast/{prediction_id}` — лента с выбранным прогнозом.

Для перехода к следующему прогнозу используется параметр:

```text
GET /forecast/{prediction_id}?next=true
```

Например:

```text
/forecast/1?next=true
```

## Фильтрация

Каталог поддерживает фильтрацию прогнозов по концентрации CO₂.

Например:

```text
/forecast/tile?co2=550
```

Получая аргумент `co2`, равный целому числу, мы создаём массив, куда складываем все опубликованные записи, у которых значение `co2_ppm` равно полученному значению `co2`, и сохраняем их в массив.

## Данные

В первой лабораторной работе база данных не используется: данные хранятся в Python-коллекции `climate_predictions`.

В коллекции присутствуют прогнозы со следующими статусами:

* `published` — опубликованный прогноз;
* `draft` — черновик;
* `deleted` — удалённый прогноз.

В каталог и ленту попадают только опубликованные прогнозы.

## Структура проекта

```text
WEB-26-WEATHER-PREDICTIONS-BACK/
├── api/
│   └── handlers.py
├── data/
│   └── collections.py
├── static/
│   └── css/
│       └── static.css
├── templates/
│   ├── add.html
│   ├── feed.html
│   ├── hotel.html
│   ├── index.html
│   └── tile.html
├── docker-compose.yml
├── main.py
└── requirements.txt
```

## Стек

* Python
* FastAPI
* Jinja2
* Uvicorn
* HTML
* CSS
* JavaScript
* Docker
* MinIO
