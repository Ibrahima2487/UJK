from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from core.models import Payment

def trone(request):
    users = User.objects.all()
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas accès à ces commissions.")
        return redirect('main')
    total_user = User.objects.count()
    paiements = Payment.objects.all()
    paiements = paiements.count()

    
    
    
    return render(request, 'trone.html', {"users" : users})

