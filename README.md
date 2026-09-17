# Kite Spot Tracker

Django + React starter for storing wind day by day and finding kiteable patterns.

This is a learning codebase, not a finished prediction product. The working pieces are the data model, one weather client, and a small fill-in calculator. The next sources and the consensus model are left for you.

## How to run

Use two terminals.

```bash
# terminal 1 — API
source .venv/bin/activate
cd backend
python manage.py migrate
python manage.py seed_spots
python manage.py ingest_weather --mode forecast
python manage.py ingest_weather --mode history --days 30
python manage.py summarize_days
python manage.py runserver
```

```bash
# terminal 2 — UI
cd frontend
npm run dev
```

Open http://localhost:5173

## What is already decided

- **Spots** own a rideable wind window. Geography first, weather second.
- **Observations** and **forecasts** are different tables. Never mix them.
- Units are **knots** and timestamps are **UTC**. Convert to the spot timezone only when you compute local fill-in.
- Open-Meteo is the first vendor because it is free, has no key, and offers forecast + ERA5 history + later GFS/ECMWF splits.

## What you should write next

1. `weather/clients/noaa_ndbc.py` — a real buoy, so you have actual wind.
2. A second Open-Meteo forecast client with `model="gfs_seamless"` or `model="ecmwf_ifs"`.
3. `patterns/ensemble.py` — average those forecasts as vectors.
4. A bias table: forecast minus observation, grouped by spot, hour, and lead time.

Do not start with machine learning. A month of honest hourly rows at two spots will teach you more than a model trained on nothing.
