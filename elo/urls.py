from django.urls import path
from . import views

urlpatterns = [
    
    path("", views.leaderboard, name="leaderboard"),

    
    path("api/v1/leaderboard/<str:gamemode>/", views.leaderboard_api, name="leaderboard_api"),
    path("api/v1/elo/set/", views.set_elo, name="set_elo"),
    path("api/v1/elo/<str:ign>/", views.get_elo, name="get_elo"),
]
