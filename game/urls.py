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
	path('2FAStatus', views.get2FAStatus),
	path('qrcode', views.getQRCode),
	path('verifyOTP', views.verifyOTP),
	path('verifyLoginOTP', views.verifyLoginOTP),
	path('updateLanguage', views.updateLanguage),
	path('getLanguague', views.getLanguagues),
	path('sitemap.xml', sitemap,  {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	path('enterQueue', views.enterQueue),
	path('enterQueueRandom', views.enterQueueRandom)
]
