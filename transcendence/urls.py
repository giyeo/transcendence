from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

urlpatterns = [
    path('', RedirectView.as_view(url='/game', permanent=True)),
    path("game/", include('game.urls')),
    path('admin/', admin.site.urls),
]