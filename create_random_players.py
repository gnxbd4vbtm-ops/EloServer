import requests
import random
import string
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, ".env"))
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("API_KEY not found in .env")
    exit(1)

# Define possible gamemodes
GAMEMODES = ["mace", "vanilla", "nethPot", "uhc", "diaPot", "sword", "axe"]

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_random_player():
    ign = generate_random_name()
    gamemode = random.choice(GAMEMODES)
    elo = random.randint(0, 5000)
    cat = random.choice(["yes", "no"])
    return ign, gamemode, elo, cat

def main():
    try:
        num_players = int(input("How many players do you want to create? "))
    except ValueError:
        print("Invalid number")
        return

    base_url = os.getenv("BASE_URL", "http://localhost:8000")  # Adjust if needed

    for i in range(num_players):
        ign, gamemode, elo, cat = create_random_player()
        data = {
            "ign": ign,
            "gamemode": gamemode,
            "elo": elo,
            "cat": cat
        }
        headers = {
            "X-API-KEY": API_KEY
        }
        try:
            response = requests.post(
                f"{base_url}/api/v1/elo/set/",
                json=data,
                headers=headers
            )
            if response.status_code == 200:
                print(f"Created player {i+1}/{num_players}: {ign} in {gamemode} with {elo} ELO")
            else:
                print(f"Failed to create player {i+1}: {response.text}")
        except Exception as e:
            print(f"Error creating player {i+1}: {e}")

if __name__ == "__main__":
    main()