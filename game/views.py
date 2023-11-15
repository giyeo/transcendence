from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from io import BytesIO
import os

import pyotp, qrcode

from django.contrib.auth import get_user_model
from .models import CustomUser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken


def index(request):
    return render(request, 'game/index.html')


INTRA_API_URL = "https://api.intra.42.fr"
INTRA_API_URL_TOKEN = INTRA_API_URL + "/oauth/token"
REDIRECT_URI = "http://127.0.0.1:8000/game"
INTRA_API_ID = "u-s4t2ud-d7f64afc7fb7dc2840609df8b5328f172dd434549cf932c6606762ecb4016c2d"
INTRA_API_SECRET = os.getenv("intra_secret")

def getToken(code):
    data = {
        "grant_type": "authorization_code",
        "client_id": INTRA_API_ID,
        "client_secret": INTRA_API_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    try:
        response = requests.post(INTRA_API_URL_TOKEN, data=data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({}, status=500)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print("Error:", response.status_code, response.text)


@api_view(['GET'])
def userData(request):
    code = request.GET.get('code')
    if code is None:
        return
    token = getToken(code)
    data = None
    url = INTRA_API_URL + "/v2/me"
    headers = {
        "Authorization": "Bearer " + token
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return JsonResponse({}, status=500)
    if r.status_code == 200:
        data = r.json()
        try:
            user = get_user_model().objects.get(username=data.get('login'))
            user_local = CustomUser.objects.get(login=data.get('login'))
        except (get_user_model().DoesNotExist, CustomUser.DoesNotExist):
            user = get_user_model().objects.create(username=data.get('login'))
            user_local = CustomUser.objects.create(login=data.get('login'))
            user.save()
            user_local.save()
        if not user_local.twofa_enabled:
            data["access_token"] = str(AccessToken.for_user(user))
        data["user_id"] = str(user.id)
    else:
        print("Error:", r.status_code, r.text)
    return JsonResponse(data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getQRCode(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    totp = pyotp.TOTP(user_local.auth_secret)
    uri = totp.provisioning_uri("localhost:8000", issuer_name="transcendence")
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png")


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def verifyOTP(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    otp = request.GET.get('otp')
    totp = pyotp.TOTP(user_local.auth_secret)
    if otp and totp.verify(otp):
        user_local.twofa_enabled = True
        user_local.save()
        return JsonResponse({}, status=200)
    return JsonResponse({}, status=403)

@api_view(['GET'])
def verifyLoginOTP(request):
    otp = request.GET.get('otp')
    user_id = request.GET.get('userId')
    user = get_user_model().objects.get(id=user_id)
    user_local = CustomUser.objects.get(id=user_id)
    if otp:
        totp = pyotp.TOTP(user_local.auth_secret)
        if totp.verify(otp):
            data = {"access_token": str(AccessToken.for_user(user))}
            return JsonResponse(data, status=200)
    return JsonResponse({}, status=403)