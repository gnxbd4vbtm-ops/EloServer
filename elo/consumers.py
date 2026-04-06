import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PlayerElo

class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_leaderboard()

    async def send_leaderboard(self):
        elos = PlayerElo.objects.select_related("player").all()

        leaderboard = {}
        gamemodes_set = set()

        for elo in elos:
            gamemodes_set.add(elo.gamemode)
            if elo.gamemode not in leaderboard:
                leaderboard[elo.gamemode] = []
            leaderboard[elo.gamemode].append({
                "ign": elo.player.ign,
                "elo": elo.elo,
                "rank": elo.rank,
                "cat": elo.cat
            })

        
        for mode in leaderboard:
            leaderboard[mode] = sorted(leaderboard[mode], key=lambda x: x["elo"], reverse=True)[:100]

        
        overall_dict = {}
        for elo in elos:
            ign = elo.player.ign
            if ign not in overall_dict:
                overall_dict[ign] = {"total": 0, "count": 0}
            overall_dict[ign]["total"] += elo.elo
            overall_dict[ign]["count"] += 1

        overall = []
        for ign, data in overall_dict.items():
            avg = data["total"] / data["count"]
            player_rank = PlayerElo.objects.filter(player__ign=ign).first()
            overall.append({
                "ign": ign,
                "elo": round(avg),
                "rank": player_rank.rank if player_rank else "",
                "cat": player_rank.cat if player_rank else ""
            })

        overall = sorted(overall, key=lambda x: x["elo"], reverse=True)[:100]
        leaderboard["Overall"] = overall
        gamemodes_set.add("Overall")

        await self.send(text_data=json.dumps({
            "leaderboard": leaderboard,
            "gamemodes": list(gamemodes_set)
        }))
