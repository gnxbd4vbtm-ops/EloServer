from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("elo.urls")),
    path('admin/', admin.site.urls),
    path('api/elo/', include('elo.urls')),
]


