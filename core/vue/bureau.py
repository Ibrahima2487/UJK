from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from core.models import Bureau
from core.forms import BureauForm

@login_required
def bureau(request):
    
    bureaux = Bureau.objects.select_related(
        'bureau_parent', 'president', 'secretaire', 'tresorier'
    ).all().order_by('niveau_hierarchique', 'nom')
    
    # Recherche simple
    search = request.GET.get('search')
    if search:
        bureaux = bureaux.filter(nom__icontains=search)
    
    context = {
        'bureaux': bureaux,
        'total_bureaux': Bureau.objects.count(),
        'bureaux_actifs': Bureau.objects.filter(statut='ACTIF').count(),
    }
    return render(request, 'bureau.html', context)



# ======== BUREAU SUPPRIME ======
from core.forms import BureauForm


@login_required
def bureau_supprime(request, id):
    bureau = get_object_or_404(Bureau, id=id)
    
    if request.method == 'POST':
        nom_bureau = bureau.nom
        bureau.delete()
        messages.success(request, f"Le bureau {nom_bureau} a été supprimé!")
        return redirect('liste_bureaux')
    
    context = {'bureau': bureau}
    return render(request, 'bureau_supprimer.html', context)

# ===== BUREAU MODIFIE ========

@login_required
def bureau_modifie(request, pk):  # Changement de 'id' à 'pk'
    bureau = get_object_or_404(Bureau, pk=pk)  # Utilisation de pk
    
    if request.method == 'POST':
        form = BureauForm(request.POST, instance=bureau)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les modifications du bureau {bureau.nom} ont été enregistrées!")
            return redirect('bureau_details', pk=bureau.pk)
    else:
        form = BureauForm(instance=bureau)
    
    context = {
        'form': form,
        'bureau': bureau,
    }
    return render(request, 'bureau_modifie.html', context)


# ======== BUREAU DETAILS ========
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


# ============= BURAU AJOUTE =====
@login_required
def bureau_ajouter(request):
    if request.method == 'POST':
        form = BureauForm(request.POST)
        if form.is_valid():
            nouveau_bureau = form.save()
            messages.success(request, f"Le bureau {nouveau_bureau.nom} a été créé avec succès!")
            return redirect('bureau')
    else:
        form = BureauForm()
    
    context = {'form': form}
    return render(request, 'bureau_ajouter.html', context)