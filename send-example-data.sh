API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Byte_Blast",
    "gamemode": "mace",
    "elo": 1852132130,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/


API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Byte_Blast",
    "gamemode": "vanilla",
    "elo": 1852132130,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/



API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Byte_Blast",
    "gamemode": "sword",
    "elo": 1852340,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/



API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Byte_Blast",
    "gamemode": "uhc",
    "elo": 1852340,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/





API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2) && curl -X POST \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ign": "Byte_Blast",
    "gamemode": "nethPot",
    "elo": 18234,
    "cat": "yes"
  }' \
  http://localhost:8000/api/v1/elo/set/