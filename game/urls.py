from django.urls import path
from . import views
from game.sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
	'static': StaticViewSitemap
}

urlpatterns = [
    path('', views.game, name='game'),
    path('data', views.userData),
    path('qrcode', views.getQRCode),
	path('verifyOTP', views.verifyOTP),
	path('verifyLoginOTP', views.verifyLoginOTP),
	path('sitemap.xml', sitemap,  {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
