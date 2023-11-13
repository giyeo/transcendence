from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/game', permanent=True)),
    path("game/", include('game.urls')),
]
