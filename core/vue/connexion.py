from django.shortcuts import render, redirect
from core.forms import AuthenticationForm
from django.contrib.auth import authenticate
from core.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AdminUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Utilisateur
from core.forms import ImageForm

def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Vous êtes maintenant connecté en tant que {username}.")
                return redirect('main')  # Redirection vers la page d'accueil
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

          # Redirection vers la page d'accueil si déjà connecté

        

        user = request.user
        if user.is_authenticated:
            return redirect('main')

    return render(request, 'connexion.html', {'form': form})