# API Examples

This file contains example curl commands and responses for all available API endpoints in the ELO Server.

**Note:** All commands assume the server is running on `http://localhost:8000`. Replace with your actual URL if different. For local self-signed certs, use `curl --cacert certs/server.crt http://localhost:8000/...` instead of `-k`.

**API Key:** Commands that require authentication load the `API_KEY` from your `.env` file. Make sure your server is running and `.env` exists.

## 1. Set Player ELO (POST /api/v1/elo/set/)

Creates or updates a player's ELO for a specific gamemode.

### Command:
```bash
API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Notch",
    "gamemode": "mace",
    "elo": 1850,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/
```

### Example Response (Success):
```json
{
    "message": "ELO updated",
    "ign": "Notch",
    "gamemode": "mace",
    "elo": 1850,
    "cat": "yes",
    "rank": 1,
    "last_updated": "2026-03-22T12:34:56Z"
}
```

### Example Response (Error - Invalid API Key):
```json
{
    "error": "Invalid API key"
}
```

### Example Response (Error - Missing Fields):
```json
{
    "error": "Missing 'ign', 'gamemode', or 'elo'"
}
```

## 2. Get Player ELO (GET /api/v1/elo/<ign>/)

Retrieves all ELO data for a specific player across all gamemodes.

### Command:
```bash
curl -s http://localhost:8000/api/v1/elo/Notch/
```

### Example Response (Success):
```json
{
    "Notch": [
        {
            "gamemode": "mace",
            "elo": 1850,
            "rank": 1,
            "cat": "yes",
            "last_updated": "2026-03-22T12:34:56Z"
        },
        {
            "gamemode": "vanilla",
            "elo": 1720,
            "rank": 3,
            "cat": "no",
            "last_updated": "2026-03-22T11:22:33Z"
        }
    ]
}
```

### Example Response (Player Not Found):
```json
{
    "error": "Player 'NonExistentPlayer' not found"
}
```

## 3. Get Leaderboard (GET /api/v1/leaderboard/<gamemode>/?page=N)

Retrieves paginated leaderboard for a specific gamemode. Each page contains 100 players.

### Command (Page 1):
```bash
curl -s "http://localhost:8000/api/v1/leaderboard/mace/?page=1"
```

### Command (Page 2):
```bash
curl -s "http://localhost:8000/api/v1/leaderboard/mace/?page=2"
```

### Example Response (mace gamemode, page 1):
```json
{
    "mace": [
        {
            "ign": "Notch",
            "elo": 1850,
            "rank": 1,
            "cat": "yes",
            "last_updated": "2026-03-22T12:34:56Z"
        },
        {
            "ign": "Steve",
            "elo": 1820,
            "rank": 2,
            "cat": "yes",
            "last_updated": "2026-03-22T10:15:30Z"
        },
        {
            "ign": "Alex",
            "elo": 1750,
            "rank": 3,
            "cat": "no",
            "last_updated": "2026-03-22T09:45:12Z"
        }
    ]
}
```

### Example Response (overall gamemode):
```bash
curl -s "http://localhost:8000/api/v1/leaderboard/overall/?page=1"
```

```json
{
    "overall": [
        {
            "ign": "Notch",
            "elo": 1785,
            "rank": 1,
            "cat": "yes",
            "last_updated": "2026-03-22T12:34:56Z"
        },
        {
            "ign": "Steve",
            "elo": 1690,
            "rank": 2,
            "cat": "no",
            "last_updated": "2026-03-22T10:15:30Z"
        }
    ]
}
```

### Example Response (Invalid Page):
```bash
curl -s "http://localhost:8000/api/v1/leaderboard/mace/?page=999"
```

```json
{
    "mace": []
}
```

## 4. Random Player Creation (Using Provided Script)

To create many random players, use the included script:

```bash
python create_random_players.py
```

This will prompt for the number of players and create them with random data.

## 5. Single Random Player (One-liner)

```bash
API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && ign=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c8) && gamemode=$(echo -e "mace\nvanilla\nnethPot\nuhc\ndiaPot\nsword\naxe" | shuf -n1) && elo=$((RANDOM % 2000)) && cat=$(echo -e "yes\nno" | shuf -n1) && curl -X POST -H "X-API-KEY: $API_KEY" -H "Content-Type: application/json" -d "{\"ign\":\"$ign\",\"gamemode\":\"$gamemode\",\"elo\":$elo,\"cat\":\"$cat\"}" http://localhost:8000/api/v1/elo/set/
```

## 6. Frontend Access

The web interface is available at:
```
http://localhost:8000/leaderboard/
```

This provides an interactive leaderboard with tabs for different gamemodes and pagination.

## Available Gamemodes

- mace
- vanilla
- nethPot
- uhc
- diaPot
- sword
- axe
- overall (computed average across all gamemodes)

## Notes

- All timestamps are in ISO format (UTC)
- `rank` is calculated per gamemode based on ELO descending
- `cat` indicates category (yes/no) - purpose depends on your use case
- Pagination starts at page 1, 100 items per page
- API responses are JSON-formatted with 4-space indentation