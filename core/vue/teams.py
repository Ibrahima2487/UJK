from django.shortcuts import render
from django.db import models


def teams(request):
    
    return render(request, 'teams.html')