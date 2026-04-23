from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from core.forms import BureauForm
from core.models import Bureau



@login_required
def bureau_details(request, pk):  # Le paramètre doit s'appeler 'pk'
    bureau = get_object_or_404(
        Bureau.objects.select_related(
            'bureau_parent', 'president', 'vice_president', 'secretaire', 
            'secretaire_adjoint', 'tresorier', 'responsable_technique', 
            'animateur_communautaire'
        ).prefetch_related('membres_actifs', 'benevoles', 'structures_filiales'), 
        pk=pk  # Ici on utilise bien 'pk'
    )
    
    context = {
        'bureau': bureau,
        'membres_dirigeants': bureau.get_membres_dirigeants(),
        'effectif_total': bureau.get_effectif_total(),
        'structures_filiales': bureau.get_structures_filiales_actives(),
        'peut_modifier': bureau.peut_modifier(request.user),
    }
    return render(request, 'bureau_details.html', context)