from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from io import BytesIO
import os

import pyotp, qrcode

from django.contrib.auth import get_user_model
from .models import CustomUser, Queue
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken


INTRA_API_URL = "https://api.intra.42.fr"
INTRA_API_URL_TOKEN = INTRA_API_URL + "/oauth/token"
INTRA_API_URL_ME = INTRA_API_URL + "/v2/me"
INTRA_API_URL_AUTH = INTRA_API_URL + "/oauth/authorize"

INTRA_REDIRECT_URI = os.environ.get('DJANGO_INTRA_REDIRECT_URI')
INTRA_API_ID = os.environ.get('DJANGO_INTRA_API_ID')
INTRA_API_SECRET = os.environ.get('DJANGO_INTRA_API_SECRET')
INTRA_RESPONSE_TYPE = "code"

API_URL = os.environ.get('DJANGO_API_URL')

def game(request):
    print("API_URL", API_URL)
    print("INTRA_API_URL_AUTH", INTRA_API_URL_AUTH)
    print("INTRA_API_ID", INTRA_API_ID)
    print("INTRA_REDIRECT_URI", INTRA_REDIRECT_URI)
    print("INTRA_RESPONSE_TYPE", INTRA_RESPONSE_TYPE)
    return render(request, 'game/index.html', {"API_URL": API_URL, "INTRA_API_URL_AUTH": INTRA_API_URL_AUTH, "INTRA_API_ID": INTRA_API_ID, "INTRA_REDIRECT_URI": INTRA_REDIRECT_URI, "INTRA_RESPONSE_TYPE": INTRA_RESPONSE_TYPE})

def getToken(code):
    data = {
        "grant_type": "authorization_code",
        "client_id": INTRA_API_ID,
        "client_secret": INTRA_API_SECRET,
        "code": code,
        "redirect_uri": INTRA_REDIRECT_URI,
    }
    print("Trying to getting a new token")
    try:
        r = requests.post(INTRA_API_URL_TOKEN, data=data)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    print("Got a new token", r.json())
    return r.json()


def getUserData(intra_access_token):
    headers = {"Authorization": "Bearer " + intra_access_token}
    url = INTRA_API_URL + "/v2/me"
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def getUserModels(login):
    try:
        user = get_user_model().objects.get(username=login)
        user_local = CustomUser.objects.get(login=login)
    except (get_user_model().DoesNotExist, CustomUser.DoesNotExist):
        user = get_user_model().objects.create(username=login)
        user_local = CustomUser.objects.create(login=login)
        user.save()
        user_local.save()
    return user, user_local


def makeNewData(data):
    new_data = {}
    new_data["login"] = data["login"]
    new_data["image"] = data["image"]
    return new_data

@api_view(['GET'])
def userData(request):
    code = request.GET.get('code')
    intra_access_token = request.GET.get('intra_access_token')
    new_data = {}
    if not intra_access_token:
        if code is None:
            return JsonResponse({"detail": "No code provided"}, status=400)
        tokenData = getToken(code)
        intra_access_token = tokenData["access_token"]
        try:
            data = getUserData(intra_access_token)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return JsonResponse({"detail": "Invalid code"}, status=401)
        new_data = makeNewData(data)
        user, user_local = getUserModels(new_data.get("login"))
        if not user_local.twofa_enabled:
            new_data["access_token"] = str(AccessToken.for_user(user))
        new_data["user_id"] = str(user.id)
        new_data["intra_access_token"] = str(intra_access_token)
    else:
        try:
            data = getUserData(intra_access_token)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return JsonResponse({"detail": "Invalid code"}, status=401)
        new_data = makeNewData(data)
        user, user_local = getUserModels(new_data.get("login"))
        if not user_local.twofa_enabled:
            new_data["access_token"] = str(AccessToken.for_user(user))
        new_data["user_id"] = str(user.id)
    return JsonResponse(new_data, status=200)


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


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getLanguagues(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    return JsonResponse({'lang': user_local.langugage})


@api_view (['PATCH'])
@permission_classes((IsAuthenticated,))
def updateLanguage(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    lang = request.GET.get('lang')
    if lang and lang in ['en', 'fr', 'pt']:
        user_local.language = lang
        user_local.save()
        return JsonResponse({'lang': user_local.language})
    return JsonResponse({}, status=400)


@api_view (['GET'])
@permission_classes((IsAuthenticated,))
def enterQueue(request):
    matchType = request.GET.get('matchType')
    gamemode = request.GET.get('gamemode')
    matchSuggestedName = request.GET.get('matchSuggestedName')
    print(request.user.id, matchType, gamemode, matchSuggestedName)
    queue = Queue.objects.create(user_id=request.user.id,
                                 login=request.user.username,
                                 match_type=matchType,
                                 gamemode=gamemode,
                                 match_suggested_name=matchSuggestedName)
    queue.save()
    #login, matchType, gamemode
    return JsonResponse({}, status=200)


@api_view (['GET'])
def enterQueueRandom(request):
    username = request.GET.get('username')
    matchType = "simpleMatch"
    gamemode = "default"
    matchSuggestedName = ""
    if not username:
        return JsonResponse({}, status=400)
    queue = Queue.objects.create(user_id=42,
                                 login=username,
                                 match_type=matchType,
                                 gamemode=gamemode,
                                 match_suggested_name=matchSuggestedName)
    queue.save()
    return JsonResponse({}, status=200)