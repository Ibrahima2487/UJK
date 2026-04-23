# views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Contact

@staff_member_required
def contact_status(request):
    """
    Vue complète pour afficher les statistiques ET tous les messages de contact
    """
    # Calculs des statistiques
   
    
    # Récupération des paramètres de recherche
    search_query = request.GET.get('search', '')
    
    # Récupération de tous les contacts avec tri par date décroissante
    contacts = Contact.objects.all().order_by('-id')
    
    # Filtrage par recherche si une requête existe
    if search_query:
        contacts = contacts.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(contenu__icontains=search_query) |
            Q(adresse__icontains=search_query)
        )
    
    # Pagination - 12 messages par page
    paginator = Paginator(contacts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        # Statistiques
        
        
        # Liste des messages
        'contacts': page_obj,
        'search_query': search_query,
        'filtered_count': contacts.count(),
        
        # Calculs supplémentaires
    
    }
    
    return render(request, 'contact_status.html', context)