from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Utilisateur

@login_required
def membre_status(request):
    # Récupérer tous les utilisateurs de base
    utilisateurs = Utilisateur.objects.all().select_related('user')
    
    # Gestion de la recherche
    search_query = request.GET.get('search', '')
    if search_query:
        utilisateurs = utilisateurs.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Gestion du filtre de statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter == 'actif':
        utilisateurs = utilisateurs.filter(user__is_active=True)
    elif statut_filter == 'inactif':
        utilisateurs = utilisateurs.filter(user__is_active=False)
    
    # Gestion du filtre de rôle
    role_filter = request.GET.get('role', '')
    if role_filter == 'admin':
        utilisateurs = utilisateurs.filter(user__is_superuser=True)
    elif role_filter == 'staff':
        utilisateurs = utilisateurs.filter(user__is_staff=True, user__is_superuser=False)
    elif role_filter == 'membre':
        utilisateurs = utilisateurs.filter(user__is_staff=False, user__is_superuser=False)
    
    # Calcul des statistiques
    total_utilisateurs = utilisateurs.count()
    utilisateurs_actifs = utilisateurs.filter(user__is_active=True).count()
    utilisateurs_inactifs = total_utilisateurs - utilisateurs_actifs
    administrateurs = utilisateurs.filter(user__is_superuser=True).count()
    staff = utilisateurs.filter(user__is_staff=True, user__is_superuser=False).count()
    
    # Pagination (optionnelle)
    # from django.core.paginator import Paginator
    # paginator = Paginator(utilisateurs, 12)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'utilisateurs': utilisateurs,  # ou page_obj si pagination
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_inactifs': utilisateurs_inactifs,
        'administrateurs': administrateurs,
        'staff': staff,
    }
    
    return render(request, 'membre_status.html', context)