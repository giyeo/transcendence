from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = [
    path('', RedirectView.as_view(url='/game', permanent=True)),
    path("game/", include('game.urls')),
    path('admin/', admin.site.urls),
]
