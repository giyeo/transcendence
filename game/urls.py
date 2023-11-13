from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data', views.userData),
    path('qrcode', views.getQRCode),
	path('verifyOTP', views.verifyOTP),
]
