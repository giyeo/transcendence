from django.shortcuts import render

# Create your views here.

def pong(request):
    return render(request, 'game/index.html')