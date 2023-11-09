from django.shortcuts import render
from django.http import JsonResponse
import requests
# Create your views here.

def pong(request):
    return render(request, 'game/index.html')

def getToken(code):
    url = "https://api.intra.42.fr/oauth/token"
    app_id = "u-s4t2ud-f7b0462e2cbc6c9ad253ff148ce9c2f02ab78c16e04b5f2351248a0f6ecc0e7f"
    secret = ""#TODO do not commit
    data = {
        "grant_type": "authorization_code",
        "client_id": app_id,
        "client_secret": secret,
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/",
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        token_data = response.json()
        print("Access Token:", token_data["access_token"])
        return token_data["access_token"]
    else:
        print("Error:", response.status_code, response.text)

def userData(request):
    code = request.GET.get('code')
    if code is not None:
        token = getToken(code)
        data = None
        url = "https://api.intra.42.fr/v2/me"
        headers = {
            "Authorization": "Bearer " + token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("User data:", data)
        else:
            print("Error:", response.status_code, response.text)
        return JsonResponse(data)
    else:
        # Handle the case when 'code' parameter is not present
        error_data = {'error': 'Missing or invalid "code" parameter'}
        return JsonResponse(error_data, status=400)