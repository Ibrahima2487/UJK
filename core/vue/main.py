# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from core.models import Publication, Commentaire, like, Utilisateur
from core.forms import CommentaireForm, PublicationForm


@login_required
def main(request):

    utilisateurs = Utilisateur.objects.all().select_related('user')
   
    # Optimisation des requêtes avec select_related et prefetch_related
    publications = Publication.objects.select_related('auteur').prefetch_related(
        Prefetch('Commentaires', 
                queryset=Commentaire.objects.select_related('auteur').order_by('-date_com')),
        Prefetch('likes', 
                queryset=like.objects.select_related('utilisateur'))
    ).annotate(
        total_likes_count=Count('likes', distinct=True),
        total_comments_count=Count('Commentaires', distinct=True)
    ).order_by('-id')
    
    # Ajout des propriétés calculées pour chaque publication
    for publication in publications:
        publication.user_has_liked = publication.likes.filter(utilisateur=request.user).exists()
        publication.total_likes = publication.total_likes_count
        publication.comments_count = publication.total_comments_count
        # Limiter les commentaires affichés initialement
        publication.limited_comments = publication.Commentaires.all()[:3]
    
    # Pagination
    paginator = Paginator(publications, 10)  # 10 publications par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "comment_form": CommentaireForm(),
        "utilisateurs" : utilisateurs,
    }
    
    return render(request, 'main.html', context)