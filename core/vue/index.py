from django.shortcuts import render, redirect
from django.contrib.auth import authenticate

def index (request):

    user = request.user
    if user.is_authenticated:
        return redirect('main')

    contexte = {
        'message' : 'Bienvenue sur la page de Bienvenue',
    }
    return render(request, 'index.html', contexte)