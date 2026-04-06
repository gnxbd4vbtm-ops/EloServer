from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Player, PlayerElo
from dotenv import load_dotenv
import os
from pathlib import Path
from django.db.models import Avg, Max


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))
API_KEY = os.getenv("API_KEY")


def rank_from_elo(elo):
    if elo < 0:
        return "has a j*b"
    elif elo < 100:
        return "a cute but dumb cat"
    elif elo < 200:
        return "Tier 09 - Combat Apprentice III"
    elif elo < 400:
        return "Tier 08-  Combat Apprentice II"
    elif elo < 600:
        return "Tier 07 - Combat Apprentice I"
    elif elo < 800:
        return "Tier 06 - Combat Adept III"
    elif elo < 1000:
        return "Tier 05 - Combat Adept II"
    elif elo < 1400:
        return "Tier 04 - Combat Adept I"
    elif elo < 1800:
        return "Tier 03 - Elite II"
    elif elo < 2200:
        return "Tier 02 - Elite I"
    elif elo < 2400:
        return "Tier 01 - Contender"
    else:
        return "get a life"


@api_view(["POST"])
def set_elo(request):
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return Response({"error": "Invalid API key"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    ign = data.get("ign")
    gamemode = data.get("gamemode")
    elo = data.get("elo")
    cat = data.get("cat", None)

    if not ign or not gamemode or elo is None:
        return Response({"error": "Missing 'ign', 'gamemode', or 'elo'"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        elo = int(elo)
    except (ValueError, TypeError):
        return Response({"error": f"Invalid ELO value: {elo}. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    
    player, _ = Player.objects.get_or_create(ign=ign)

    
    player_elo, _ = PlayerElo.objects.get_or_create(
        player=player,
        gamemode=gamemode,
        defaults={'elo': elo, 'cat': str(cat) if cat is not None else 'no'}
    )

    
    player_elo.elo = elo
    if cat is not None:
        player_elo.cat = str(cat)
    player_elo.save()

    
    cache.clear()

    return Response({
        "message": "ELO updated",
        "ign": player.ign,
        "gamemode": gamemode,
        "elo": player_elo.elo,
        "cat": player_elo.cat,
        "rank": player_elo.rank,
        "last_updated": player_elo.last_updated
    })


@cache_page(300)
@api_view(["GET"])
def get_elo(request, ign):
    try:
        player = Player.objects.get(ign=ign)
    except Player.DoesNotExist:
        return Response({"error": f"Player '{ign}' not found"}, status=status.HTTP_404_NOT_FOUND)

    elos = player.elos.all()
    response = [
        {
            "gamemode": e.gamemode,
            "elo": e.elo,
            "rank": e.rank,
            "cat": e.cat,
            "last_updated": e.last_updated
        } for e in elos
    ]
    return Response({player.ign: response})


from django.core.paginator import Paginator


@cache_page(300)
def leaderboard_api(request, gamemode):
    page = request.GET.get('page', 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    
    items_per_page = 100
    
    
    if gamemode.lower() == "overall":
        cache_key = f"leaderboard_overall_page_{page}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return JsonResponse({gamemode: cached_result})

        aggregated = (
            PlayerElo.objects.values("player__ign")
            .annotate(avg_elo=Avg("elo"), cat=Max("cat"), last_updated=Max("last_updated"))
            .order_by("-avg_elo")
        )
        paginator = Paginator(aggregated, items_per_page)
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)

        result = [
            {
                "ign": row["player__ign"],
                "elo": float(round(row["avg_elo"], 2)),
                "rank": rank_from_elo(row["avg_elo"]),
                "cat": row["cat"],
                "last_updated": row["last_updated"],
            }
            for row in page_obj
        ]
        cache.set(cache_key, result, 300)
        return JsonResponse({gamemode: result})

    
    players_qs = PlayerElo.objects.filter(gamemode__iexact=gamemode).order_by("-elo")
    paginator = Paginator(players_qs, items_per_page)
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    result = []
    for e in page_obj:
        result.append({
            "ign": e.player.ign,
            "elo": e.elo,
            "rank": e.rank,
            "cat": e.cat,
            "last_updated": e.last_updated
        })
    return JsonResponse({gamemode: result})

@cache_page(300)
def leaderboard(request):
    return render(request, "leaderboard.html")
