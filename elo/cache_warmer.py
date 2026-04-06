import logging
import math
import os
import sys
import threading
import time

from django.test import RequestFactory
from django.conf import settings
from django.db.models import Count

logger = logging.getLogger(__name__)
_warmer_started = False
_warmer_lock = threading.Lock()
PAGE_SIZE = 100
WARM_INTERVAL_SECONDS = 30
WARM_EXCLUDE_COMMANDS = {
    "migrate",
    "makemigrations",
    "collectstatic",
    "shell",
    "dbshell",
    "test",
    "flush",
    "inspectdb",
}


def _is_runserver_child():
    return settings.DEBUG and os.environ.get("RUN_MAIN") == "true"


def _should_start_warmer():
    if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
        return False
    if len(sys.argv) > 1 and sys.argv[1] in WARM_EXCLUDE_COMMANDS:
        return False
    return True


def _warm_leaderboard_cache():
    from . import views
    from .models import Player, PlayerElo

    factory = RequestFactory()

    def _cache_path(path, view, *args):
        request = factory.get(path)
        try:
            view(request, *args)
        except Exception:
            logger.exception("Cache warmer failed for %s", path)

    
    _cache_path("/leaderboard/", views.leaderboard)

    
    total_players = Player.objects.count()
    overall_pages = math.ceil(total_players / PAGE_SIZE) if total_players else 1
    for page in range(1, overall_pages + 1):
        _cache_path(f"/api/v1/leaderboard/overall/?page={page}", views.leaderboard_api, "overall")

    
    gamemodes = PlayerElo.objects.values_list("gamemode", flat=True).distinct()
    for gamemode in gamemodes:
        count = PlayerElo.objects.filter(gamemode__iexact=gamemode).count()
        pages = math.ceil(count / PAGE_SIZE) if count else 1
        for page in range(1, pages + 1):
            _cache_path(
                f"/api/v1/leaderboard/{gamemode}/?page={page}",
                views.leaderboard_api,
                gamemode,
            )


def _run_warmer_loop():
    logger.info("Starting leaderboard cache warmer thread")
    while True:
        try:
            _warm_leaderboard_cache()
        except Exception:
            logger.exception("Unhandled error in cache warmer loop")
        time.sleep(WARM_INTERVAL_SECONDS)


def start_cache_warmer():
    global _warmer_started
    with _warmer_lock:
        if _warmer_started:
            return
        if not _should_start_warmer():
            return

        thread = threading.Thread(target=_run_warmer_loop, daemon=True, name="elo-cache-warmer")
        thread.start()
        _warmer_started = True
