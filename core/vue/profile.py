from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from decimal import Decimal
from core.models import Utilisateur, Payment, Affectation, Publication, Reunion, Projet, HistoriquePaiement, Message


@login_required
def profile(request):
    """
    Tableau de bord complet de l'utilisateur connecté.
    """
    # Récupère le profil étendu (OneToOne avec User)
    utilisateur = get_object_or_404(Utilisateur, user=request.user)

    # ========== COTISATIONS / PAIEMENTS ==========
    cotisations = Payment.objects.filter(utilisateur=request.user).select_related('caisse')

    total_paye = (
        cotisations.filter(status='paye').aggregate(total=Sum('montant'))['total']
        or Decimal('0')
    )
    total_attente = (
        cotisations.filter(status='en_attente').aggregate(total=Sum('montant'))['total']
        or Decimal('0')
    )
    total_retard = (
        cotisations.filter(status='retard').aggregate(total=Sum('montant'))['total']
        or Decimal('0')
    )
    nb_en_attente = cotisations.filter(status='en_attente').count()

    total_global = total_paye + total_attente + total_retard
    taux_paiement = (
        float(total_paye / total_global * 100) if total_global > 0 else 0.0
    )

    # ========== BUREAUX & AFFECTATIONS ==========
    affectations = (
        Affectation.objects.filter(membre=utilisateur, actif=True)
        .select_related('bureau')
        .order_by('-date_affectation')
    )

    # ========== PUBLICATIONS ==========
    publications = (
        Publication.objects.filter(auteur=request.user)
        .prefetch_related('Commentaires', 'likes')
        .order_by('-date_creation')[:10]
    )

    # ========== RÉUNIONS ==========
    reunions = (
        Reunion.objects.filter(participants=request.user)
        .order_by('-date_reunion')[:10]
    )

    # ========== PROJETS (où l'utilisateur est responsable) ==========
    projets = (
        Projet.objects.filter(responsable=request.user)
        .order_by('-date_debut')[:10]
    )

    # ========== HISTORIQUE VALIDATIONS ==========
    historique_paiements = (
        HistoriquePaiement.objects.filter(
            cotisation__utilisateur=request.user
        )
        .select_related('cotisation')
        .order_by('-date_action')[:20]
    )

    # ========== MESSAGES RÉCENTS (messagerie globale) ==========
    messages_recents = (
        Message.objects.all()
        .select_related('envoyeur')
        .order_by('-date_envoi')[:15]
    )

    context = {
        'utilisateur': utilisateur,
        'cotisations': cotisations,
        'total_paye': total_paye,
        'total_attente': total_attente,
        'total_retard': total_retard,
        'nb_en_attente': nb_en_attente,
        'taux_paiement': round(taux_paiement, 1),
        'affectations': affectations,
        'publications': publications,
        'reunions': reunions,
        'projets': projets,
        'historique_paiements': historique_paiements,
        'messages_recents': messages_recents,
    }

    return render(request, 'profile.html', context)