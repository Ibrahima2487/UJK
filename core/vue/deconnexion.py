from django.shortcuts import render, redirect
from core.forms import AuthenticationForm
from django.contrib.auth import authenticate
from core.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AdminUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm



def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('connexion')