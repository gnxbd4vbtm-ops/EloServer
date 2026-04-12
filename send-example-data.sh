API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2)

GAMEMODES=("mace" "vanilla" "nethPot" "uhc" "diaPot" "sword" "axe")

for gm in "${GAMEMODES[@]}"; do
  curl -s -X POST \
    -H "X-API-KEY: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"ign\": \"Byte_Blast\",
      \"gamemode\": \"$gm\",
      \"elo\": 1852340,
      \"cat\": \"yes\"
    }" \
    http://localhost:8000/api/v1/elo/set/
  echo " -> $gm done"
done