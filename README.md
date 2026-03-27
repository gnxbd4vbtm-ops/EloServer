# ELO Server Setup Guide

This document explains how to set up and run the Minecraft ELO leaderboard server end-to-end, including new PostgreSQL database setup, API usage, and admin utilities.

## 1) What this project contains

- Django web app (`elosystem/`, `elo/`) with REST API.
- Leaderboard frontend at `/leaderboard/` (HTML + JS).
- API endpoint versioned under `/api/v1/`:
  - `GET /api/v1/leaderboard/<gamemode>/?page=N`
  - `POST /api/v1/elo/set/` (with `X-API-KEY` in header)
  - `GET /api/v1/elo/<ign>/`
- ELO model built around `Player` and `PlayerElo`.

## 2) Required tools

- Python 3.11+ (or 3.10)
- PostgreSQL server (13+)
- `pip` (for dependencies)
- `git` (optional)

## 3) Database naming and credentials

Current defaults in `elosystem/settings.py`:

- Database name: `elo_db`
- Database user: `byte.blast`
- Database password: from `.env` variable `POSTGRES_PASSWORD`
- API key: from `.env` variable `API_KEY`
- Django secret key: from `.env` variable `SECRET_KEY`

The setup script in this repo lets you customize these.

## 4) Setup steps (manual)

I recommend doing all of this in an virtual env.

1. Create `.env` in project root

```ini
SECRET_KEY=change_me_to_very_long_random_value
API_KEY=change_me_to_very_long_random_value
POSTGRES_PASSWORD=change_me_to_very_long_random_value
```

2. Install dependencies

```bash
python -m pip install -U pip
pip install -r requirements.txt
```

3. Create/Reset PostgreSQL user+db (as PostgreSQL superuser):

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS elo_db;"
sudo -u postgres psql -c "DROP USER IF EXISTS \"byte.blast\";"
sudo -u postgres psql -c "CREATE USER \"byte.blast\" WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE elo_db OWNER \"byte.blast\";"
```

4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run server

```bash
python manage.py runserver
```

## 5) API usage

### Leaderboard pages
- `/api/v1/leaderboard/mace/?page=1`
- `/api/v1/leaderboard/overall/?page=2`

### Set player ELO
- `POST /api/v1/elo/set/` body JSON:
  - `ign`: string
  - `gamemode`: string
  - `elo`: int
  - `cat`: `yes` / `no` (optional)

Headers:
- `X-API-KEY: <your API key>`

### Get single player ELO
- `GET /api/v1/elo/<ign>/`

## 6) tiers & ranking

- API returns `rank` from `PlayerElo.rank` and `elo`.
- UI sorts by ELO desc.
- `overall` is computed as player average ELO across gamemodes.

## 7) Automation script (recommended)

Run the helper script:

```bash
bash setup_server.sh
```

It will ask:
- PostgreSQL superuser command prefix (defaults to `sudo -u postgres`)
- Database name (default `elo_db`)
- DB user (default `byte.blast`)
- DB password (random, if blank)
- Django SECRET_KEY / API_KEY (random, if blank)

Then it will create/drop DB and user, write `.env`, install Python packages, run migrations.

---

## 8) Notes

- This system now uses `/api/v1/` endpoints so future versioning (`/api/v2/`) is easy.
- Always keep your `.env` out of source control.
- Use this example command for a page 1 request for `mace`:

```bash
curl -s "http://localhost:8000/api/v1/leaderboard/mace/?page=1"
```
