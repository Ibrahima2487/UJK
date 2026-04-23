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

"""

# Détails d'un bureau spécifique
@login_required


# Créer un nouveau bureau


# Modifier un bureau existant


# Supprimer un bureau
@login_required
def supprimer_bureau(request, id):
    bureau = get_object_or_404(Bureau, id=id)
    
    if request.method == 'POST':
        nom_bureau = bureau.nom
        bureau.delete()
        messages.success(request, f"Le bureau {nom_bureau} a été supprimé!")
        return redirect('liste_bureaux')
    
    context = {'bureau': bureau}
    return render(request, 'bureau/supprimer.html', context)

# Tableau de bord avec statistiques
@login_required
def tableau_de_bord(request):
    # Statistiques de base
    total_bureaux = Bureau.objects.count()
    bureaux_actifs = Bureau.objects.filter(statut='ACTIF').count()
    
    # Répartition par type
    repartition_type = {}
    for type_code, type_nom in Bureau.TYPE_BUREAU_CHOICES:
        count = Bureau.objects.filter(type_bureau=type_code).count()
        repartition_type[type_nom] = count
    
    context = {
        'total_bureaux': total_bureaux,
        'bureaux_actifs': bureaux_actifs,
        'repartition_type': repartition_type,
    }
    
    return render(request, 'bureau/tableau_de_bord.html', context)

# Structure organisationnelle
@login_required
def structure_organisationnelle(request):
    # Trouver le bureau principal (racine)
    bureau_principal = Bureau.objects.filter(type_bureau='PRINCIPAL').first()
    
    context = {
        'bureau_principal': bureau_principal,
    }
    
    return render(request, 'bureau/structure.html', context)

# Générer un rapport pour un bureau
@login_required
def generer_rapport(request, id):
    bureau = get_object_or_404(Bureau, id=id)
    rapport = bureau.generer_rapport_communautaire()
    
    return JsonResponse(rapport)

"""



""""
# views.py - CRUD Bureau Essentiel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Bureau
from .forms import BureauForm





@login_required
def bureau_detail(request, pk):
    
    bureau = get_object_or_404(
        Bureau.objects.select_related(
            'bureau_parent', 'president', 'vice_president', 'secretaire', 
            'secretaire_adjoint', 'tresorier', 'responsable_technique', 
            'animateur_communautaire'
        ).prefetch_related('membres_actifs', 'benevoles', 'structures_filiales'), 
        pk=pk
    )
    
    context = {
        'bureau': bureau,
        'membres_dirigeants': bureau.get_membres_dirigeants(),
        'effectif_total': bureau.get_effectif_total(),
        'structures_filiales': bureau.get_structures_filiales_actives(),
        'peut_modifier': bureau.peut_modifier(request.user),
    }
    return render(request, 'bureau_detail.html', context)


@login_required
def bureau_create(request):
    
    if request.method == 'POST':
        form = BureauForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    bureau = form.save()
                    messages.success(
                        request, 
                        f'Le bureau "{bureau.nom}" a été créé avec succès!'
                    )
                    return redirect('bureau:detail', pk=bureau.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
    else:
        form = BureauForm()
    
    context = {
        'form': form,
        'title': 'Créer un nouveau bureau',
        'button_text': 'Créer le bureau'
    }
    return render(request, 'bureau/bureau_form.html', context)


@login_required
def bureau_update(request, pk):
    
    bureau = get_object_or_404(Bureau, pk=pk)
    
    # Vérifier les permissions
    if not bureau.peut_modifier(request.user):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce bureau.")
        return redirect('bureau:detail', pk=pk)
    
    if request.method == 'POST':
        form = BureauForm(request.POST, instance=bureau)
        if form.is_valid():
            try:
                with transaction.atomic():
                    bureau = form.save()
                    messages.success(
                        request, 
                        f'Le bureau "{bureau.nom}" a été modifié avec succès!'
                    )
                    return redirect('bureau:detail', pk=bureau.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
    else:
        form = BureauForm(instance=bureau)
    
    context = {
        'form': form,
        'bureau': bureau,
        'title': f'Modifier {bureau.nom}',
        'button_text': 'Enregistrer les modifications'
    }
    return render(request, 'bureau/bureau_form.html', context)


@login_required
def bureau_delete(request, pk):
   
    bureau = get_object_or_404(Bureau, pk=pk)
    
    # Vérifier les permissions
    if not bureau.peut_modifier(request.user):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce bureau.")
        return redirect('bureau:detail', pk=pk)
    
    if request.method == 'POST':
        # Vérifier s'il y a des structures filiales
        if bureau.structures_filiales.exists():
            messages.error(
                request, 
                f'Impossible de supprimer "{bureau.nom}" car il a des structures filiales associées.'
            )
            return redirect('bureau:detail', pk=pk)
        
        try:
            with transaction.atomic():
                nom_bureau = bureau.nom
                bureau.delete()
                messages.success(
                    request, 
                    f'Le bureau "{nom_bureau}" a été supprimé avec succès.'
                )
                return redirect('bureau:list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            return redirect('bureau:detail', pk=pk)
    
    context = {
        'bureau': bureau,
        'structures_filiales': bureau.structures_filiales.all(),
    }
    return render(request, 'bureau/bureau_confirm_delete.html', context)
    """