from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.pong),
	path('data', views.userData),
    path('qrcode', views.getQRCode),
	path('verifyOTP', views.verifyOTP)
]
