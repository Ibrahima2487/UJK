from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from decimal import Decimal
import json
from django.db import models


@login_required
def vue_classeur(request, pk):
    """Vue principale du classeur (comme Excel)"""
    classeur = get_object_or_404(Classeur, pk=pk)
    
    # Vérifier les permissions
    if not (classeur.proprietaire == request.user or request.user in classeur.partage_avec.all()):
        messages.error(request, "Vous n'avez pas accès à ce classeur")
        return redirect('comptabilite:liste_classeurs')
    
    feuilles = classeur.feuilles.filter(visible=True).order_by('ordre')
    feuille_active = feuilles.first() if feuilles.exists() else None
    
    if request.GET.get('feuille_id'):
        feuille_active = get_object_or_404(Feuille, id=request.GET.get('feuille_id'), classeur=classeur)
    
    context = {
        'classeur': classeur,
        'feuilles': feuilles,
        'feuille_active': feuille_active,
    }
    
    return render(request, 'compta_classeur.html', context)