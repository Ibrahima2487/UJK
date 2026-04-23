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








"""
@login_required
@require_POST
@csrf_protect
def add_comment(request, pk):
  
    publication = get_object_or_404(Publication, pk=pk)
    form = CommentaireForm(request.POST)
    
    if form.is_valid():
        commentaire = form.save(commit=False)
        commentaire.auteur = request.user
        commentaire.publication = publication
        commentaire.save()
        
        # Réponse AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': commentaire.id,
                    'auteur': commentaire.auteur.username,
                    'auteur_initials': commentaire.auteur.username[:2].upper(),
                    'texte': commentaire.texte,
                    'date_com': commentaire.date_com.strftime('%d %b %Y à %H:%M'),
                    'date_relative': commentaire.date_com
                },
                'total_comments': publication.Commentaires.count()
            })
        
        messages.success(request, "Commentaire ajouté avec succès !")
        return redirect("main")
    else:
        # Gestion des erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        
        messages.error(request, "Erreur lors de l'ajout du commentaire.")
        return redirect("main")

@login_required
@require_POST
@csrf_protect
def toggle_like(request, pk):
   
    publication = get_object_or_404(Publication, pk=pk)
    
    # Vérifier si l'utilisateur a déjà liké cette publication
    existing_like = like.objects.filter(
        publication=publication,
        utilisateur=request.user
    ).first()
    
    if existing_like:
        # Supprimer le like existant
        existing_like.delete()
        liked = False
        message = "Like retiré"
    else:
        # Créer un nouveau like
        like.objects.create(
            publication=Publication,
            utilisateur=request.user
        )
        liked = True
        message = "Publication likée"
    
    # Calculer le nouveau nombre de likes
    total_likes = publication.total_likes()
    
    # Réponse AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_likes,
            'message': message
        })
    
    # Fallback pour les navigateurs sans JavaScript
    messages.success(request, message)
    return redirect("main")

@login_required
def load_more_comments(request, pk):
    
    publication = get_object_or_404(Publication, pk=pk)
    offset = int(request.GET.get('offset', 0))
    limit = 5
    
    commentaires = publication.Commentaires.select_related('auteur').order_by('-date_com')[offset:offset+limit]
    
    comments_data = [{
        'id': c.id,
        'auteur': c.auteur.username,
        'auteur_initials': c.auteur.username[:2].upper(),
        'texte': c.texte,
        'date_com': c.date_com.strftime('%d %b %Y à %H:%M'),
        'date_relative': c.date_com
    } for c in commentaires]
    
    return JsonResponse({
        'comments': comments_data,
        'has_more': publication.Commentaires.count() > offset + limit
    })
"""