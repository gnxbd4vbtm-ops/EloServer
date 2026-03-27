from django.urls import path
from . import views

urlpatterns = [
    # this is just the main page
    path("leaderboard/", views.leaderboard, name="leaderboard"),

    # API v1 routes
    path("api/v1/leaderboard/<str:gamemode>/", views.leaderboard_api, name="leaderboard_api"),
    path("api/v1/elo/set/", views.set_elo, name="set_elo"),
    path("api/v1/elo/<str:ign>/", views.get_elo, name="get_elo"),
]
