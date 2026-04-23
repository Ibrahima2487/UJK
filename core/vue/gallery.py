from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q  # <-- Ajout de l'import manquant
from core.models import albums


def gallery(request):
    """Vue principale pour afficher tous les albums avec filtres et pagination"""
    
    # Récupération des paramètres de filtrage
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-date_created')
    
    # Filtrage de base
    albums_list = albums.objects.all()
    
    # Filtre par catégorie
    if category_filter:
        albums_list = albums_list.filter(category=category_filter)
    
    # Filtre par recherche
    if search_query:
        albums_list = albums_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Tri
    valid_sorts = ['-date_created', 'date_created', 'title', '-title']
    if sort_by in valid_sorts:
        albums_list = albums_list.order_by(sort_by)
    else:
        albums_list = albums_list.order_by('-date_created')
    
    # Pagination - 12 albums par page
    paginator = Paginator(albums_list, 12)
    page = request.GET.get('page')
    
    try:
        albums_page = paginator.page(page)
    except PageNotAnInteger:
        albums_page = paginator.page(1)
    except EmptyPage:
        albums_page = paginator.page(paginator.num_pages)
    
    # Statistiques par catégorie pour les filtres
    categories_stats = {}
    for choice_value, choice_label in albums.CATEGORY_CHOICES:
        count = albums.objects.filter(category=choice_value).count()
        categories_stats[choice_value] = {
            'label': choice_label,
            'count': count,
            'active': choice_value == category_filter
        }
    
    # Options de tri
    sort_options = [
        {'value': '-date_created', 'label': 'Plus récent'},
        {'value': 'date_created', 'label': 'Plus ancien'},
        {'value': 'title', 'label': 'Titre A-Z'},
        {'value': '-title', 'label': 'Titre Z-A'},
    ]
    
    # Construction des paramètres d'URL pour la pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'albums': albums_page,
        'categories': albums.CATEGORY_CHOICES,
        'categories_stats': categories_stats,
        'current_category': category_filter,
        'search_query': search_query,
        'current_sort': sort_by,
        'sort_options': sort_options,
        'total_albums': albums_list.count(),
        'filtered_count': albums_list.count(),
        'query_params': query_params.urlencode(),
        'title': 'Galerie d\'Albums'
    }
    
    return render(request, 'gallery.html', context)