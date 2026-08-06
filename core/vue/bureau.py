from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from core.models import Bureau, Affectation
from core.forms import BureauForm, AffectationForm, MessageBureauForm


# ============= LISTE DES BUREAUX =============
@login_required
def bureau(request):
    """
    Portail des Bureaux : redirige directement si le membre n'a qu'une seule
    Affectation active, sinon affiche la liste (avec ses bureaux accessibles
    mis en avant : affectation directe OU visite via un bureau central).
    """
    profil = getattr(request.user, 'utilisateur', None)

    # Redirection directe si le membre n'a qu'un seul Bureau affecté
    if profil:
        bureau_unique = profil.bureau_redirection()
        if bureau_unique and not request.GET.get('liste'):
            return redirect('bureau_details', pk=bureau_unique.pk)

    bureaux = Bureau.objects.annotate(
        effectif=Count('affectations', filter=Q(affectations__actif=True), distinct=True)
    ).order_by('type_bureau')

    search = request.GET.get('search')
    if search:
        bureaux = bureaux.filter(nom__icontains=search)

    # Marque, pour l'affichage, quels bureaux sont accessibles à l'utilisateur courant
    bureaux_accessibles = {b.pk for b in bureaux if b.utilisateur_a_acces(request.user)}

    context = {
        'bureaux': bureaux,
        'bureaux_accessibles': bureaux_accessibles,
        'total_bureaux': Bureau.objects.count(),
        'peut_affecter': Bureau.peut_affecter_membres(request.user),
    }
    return render(request, 'bureau.html', context)


# ======== BUREAU SUPPRIMÉ ========
@login_required
def bureau_supprime(request, pk):
    bureau_obj = get_object_or_404(Bureau, pk=pk)

    # Seuls les responsables de Logistique/Exécutif gèrent la structure des Bureaux
    if not Bureau.peut_affecter_membres(request.user) and not request.user.is_superuser:
        return HttpResponseForbidden("Action réservée aux responsables Logistique/Exécutif.")

    if request.method == 'POST':
        nom_bureau = bureau_obj.nom
        bureau_obj.delete()
        messages.success(request, f"Le bureau {nom_bureau} a été supprimé !")
        return redirect('bureau')

    context = {'bureau': bureau_obj}
    return render(request, 'bureau_supprimer.html', context)


# ===== BUREAU MODIFIÉ ========
@login_required
def bureau_modifie(request, pk):
    bureau_obj = get_object_or_404(Bureau, pk=pk)

    if not Bureau.peut_affecter_membres(request.user) and not request.user.is_superuser:
        return HttpResponseForbidden("Action réservée aux responsables Logistique/Exécutif.")

    if request.method == 'POST':
        form = BureauForm(request.POST, instance=bureau_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les modifications du bureau {bureau_obj.nom} ont été enregistrées !")
            return redirect('bureau_details', pk=bureau_obj.pk)
    else:
        form = BureauForm(instance=bureau_obj)

    context = {'form': form, 'bureau': bureau_obj}
    return render(request, 'bureau_modifie.html', context)


# ======== BUREAU DÉTAILS (avec chat interne) ========
@login_required
def bureau_details(request, pk):
    bureau_obj = get_object_or_404(
        Bureau.objects.prefetch_related('affectations__membre__user'), pk=pk
    )

    # Accès : membre affecté directement, ou visiteur via un bureau central
    a_acces = bureau_obj.utilisateur_a_acces(request.user)
    if not a_acces and not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas accès à ce Bureau.")
        return redirect('bureau')

    peut_publier = bureau_obj.utilisateur_peut_publier(request.user)

    # Envoi d'un message dans le chat du Bureau (même vue, POST-Redirect-GET)
    if request.method == 'POST':
        if not peut_publier:
            return HttpResponseForbidden(
                "Accès en lecture seule : seuls les membres affectés à ce Bureau peuvent écrire."
            )
        chat_form = MessageBureauForm(request.POST, request.FILES)
        if chat_form.is_valid():
            message = chat_form.save(commit=False)
            message.bureau = bureau_obj
            message.auteur = request.user
            message.full_clean()  # déclenche MessageBureau.clean()
            message.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'auteur': str(request.user),
                    'contenu': message.contenu,
                })
            return redirect('bureau_details', pk=bureau_obj.pk)
        else:
            messages.error(request, "Message invalide, réessayez.")
            return redirect('bureau_details', pk=bureau_obj.pk)

    affectations_actives = bureau_obj.affectations.filter(actif=True).select_related('membre__user')

    # order_by('-date_envoi')[:50] prend les 50 PLUS RÉCENTS,
    # reversed() les remet en ordre chronologique croissant pour l'affichage
    derniers_messages = list(reversed(
        bureau_obj.messages.select_related('auteur').order_by('-date_envoi')[:50]
    )) if a_acces else []

    context = {
        'bureau': bureau_obj,
        'membres': affectations_actives,
        'responsables': affectations_actives.filter(est_responsable=True),
        'effectif_total': affectations_actives.count(),
        'peut_modifier': Bureau.peut_affecter_membres(request.user) or request.user.is_superuser,
        'peut_affecter': Bureau.peut_affecter_membres(request.user),
        'peut_publier': peut_publier,
        # Lecture seule pour les visiteurs des bureaux centraux : accès mais pas d'écriture
        'lecture_seule': a_acces and not peut_publier,
        'messages_bureau': derniers_messages,
    }
    return render(request, 'bureau_details.html', context)


# ============= BUREAU AJOUTER =====
@login_required
def bureau_ajouter(request):
    if not Bureau.peut_affecter_membres(request.user) and not request.user.is_superuser:
        return HttpResponseForbidden("Action réservée aux responsables Logistique/Exécutif.")

    if request.method == 'POST':
        form = BureauForm(request.POST)
        if form.is_valid():
            nouveau_bureau = form.save()
            messages.success(request, f"Le bureau {nouveau_bureau.nom} a été créé avec succès !")
            return redirect('bureau')
    else:
        form = BureauForm()

    context = {'form': form}
    return render(request, 'bureau_ajouter.html', context)


# ============= AFFECTER UN MEMBRE (formulaire réservé Logistique/Exécutif) =====
@login_required
def bureau_affecter(request, pk):
    bureau_obj = get_object_or_404(Bureau, pk=pk)

    if not Bureau.peut_affecter_membres(request.user):
        return HttpResponseForbidden(
            "Seul un responsable du Bureau Logistique ou Exécutif peut affecter un membre."
        )

    if request.method == 'POST':
        form = AffectationForm(request.POST)
        if form.is_valid():
            affectation = form.save(commit=False)
            affectation.bureau = bureau_obj
            affectation.affecte_par = request.user
            affectation.full_clean()  # déclenche Affectation.clean()
            affectation.save()
            messages.success(
                request,
                f"{affectation.membre} affecté(e) au {bureau_obj.nom} en tant que {affectation.poste}."
            )
            return redirect('bureau_details', pk=bureau_obj.pk)
    else:
        form = AffectationForm(initial={'bureau': bureau_obj})

    context = {'form': form, 'bureau': bureau_obj}
    return render(request, 'bureau_affecter.html', context)