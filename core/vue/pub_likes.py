from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from core.models import like


@login_required
@require_POST
@csrf_protect
def pub_likes(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    form = likeForm(request.POST)
    if request.method =="POST":
        if form.is_valid():
            aime = form.save(commit=False)
            aime.auteur = request.user
            aime.publication = publication
            aime.save()
            return redirect("main")
    else:
        form = CommentaireForm()
    return render(request, 'pub_likes.html', {"form" : form })


"""  
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
"""