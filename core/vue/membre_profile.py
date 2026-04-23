from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db import models
from core.forms import UserForm
from core.models import Utilisateur

@login_required
def membre_profile(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, user__id=user_id)
    
    context = {
        'utilisateur': utilisateur
    }
    return render(request, 'membre_profile.html', context)