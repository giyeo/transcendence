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
WS_URL = os.environ.get('DJANGO_WS_URL')

def game(request):
    return render(request, 'game/index.html', {"API_URL": API_URL, "WS_URL": WS_URL, "INTRA_API_URL_AUTH": INTRA_API_URL_AUTH, "INTRA_API_ID": INTRA_API_ID, "INTRA_REDIRECT_URI": INTRA_REDIRECT_URI, "INTRA_RESPONSE_TYPE": INTRA_RESPONSE_TYPE})

def getToken(code):
    data = {
        "grant_type": "authorization_code",
        "client_id": INTRA_API_ID,
        "client_secret": INTRA_API_SECRET,
        "code": code,
        "redirect_uri": INTRA_REDIRECT_URI,
    }
    try:
        r = requests.post(INTRA_API_URL_TOKEN, data=data)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
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
def get2FAStatus(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    return JsonResponse({'twofa_enabled': user_local.twofa_enabled})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getQRCode(request):
    try:
        user_local = CustomUser.objects.get(id=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({}, status=403)
    totp = pyotp.TOTP(user_local.auth_secret)
    uri = totp.provisioning_uri(name=user_local.login, issuer_name="transcendence")
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
    if not otp or not otp.isdigit() or len(otp) > 6:
        return JsonResponse({}, status=403)
    totp = pyotp.TOTP(user_local.auth_secret)
    if totp.verify(otp):
        if user_local.twofa_enabled:
            user_local.twofa_enabled = False
            user_local.auth_secret = pyotp.random_base32()
            user_local.save()
            return JsonResponse({"twofa_enabled": False}, status=200)
        else:
            user_local.twofa_enabled = True
            user_local.save()
            return JsonResponse({"twofa_enabled": True}, status=200)
    else:
        return JsonResponse({}, status=403)

@api_view(['GET'])
def verifyLoginOTP(request):
    otp = request.GET.get('otp')
    if not otp or not otp.isdigit() or len(otp) > 6:
        return JsonResponse({}, status=403)
    user_id = request.GET.get('userId')
    if not user_id or not user_id.isdigit():
        return JsonResponse({}, status=403)
    user = get_user_model().objects.get(id=user_id)
    user_local = CustomUser.objects.get(id=user_id)
    totp = pyotp.TOTP(user_local.auth_secret)
    if totp.verify(otp):
        data = {"access_token": str(AccessToken.for_user(user))}
        return JsonResponse(data, status=200)
    else:
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
    if matchType:
        if (matchType != "simpleMatch" and matchType != "tournamentMatch" and matchType != "tournamentMatchFinal"):
            return JsonResponse({}, status=400)
    else:
        matchType = "simpleMatch"
    gamemode = request.GET.get('gamemode')
    if gamemode:
        if (gamemode != "defaultGameMode" and gamemode != "crazyGameMode"):
            return JsonResponse({}, status=400)
    else:
        gamemode = "defaultGameMode"

    if (matchType == "tournamentMatch" and gamemode == "crazyGameMode"):
        return JsonResponse({}, status=400)

    matchSuggestedName = request.GET.get('matchSuggestedName')
    if matchSuggestedName:
        if (len(matchSuggestedName) > 32):
            return JsonResponse({}, status=400)
        if not matchSuggestedName.isalpha():
            return JsonResponse({}, status=400)
    else:
        matchSuggestedName = ""

    alias = request.GET.get('alias')
    if alias:
        if (len(alias) > 12):
            return JsonResponse({}, status=400)
        if not alias.isalpha():
            return JsonResponse({}, status=400)

    try:
        queue = Queue.objects.create(user_id=request.user.id,
                                    login=request.user.username,
                                    match_type=matchType,
                                    gamemode=gamemode,
                                    match_suggested_name=matchSuggestedName,
                                    alias=alias)
        queue.save()
    except Exception as e:
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)


@api_view (['GET'])
def enterQueueRandom(request):
    username = request.GET.get('username')
    if username:
        if (len(username) > 32):
            return JsonResponse({}, status=400)
    else:
        return JsonResponse({}, status=400)
    matchType = "simpleMatch"
    gamemode = "defaultGameMode"
    matchSuggestedName = ""
    try:
        queue = Queue.objects.create(user_id=42,
                                    login=username,
                                    match_type=matchType,
                                    gamemode=gamemode,
                                    match_suggested_name=matchSuggestedName)
        queue.save()
    except Exception as e:
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)