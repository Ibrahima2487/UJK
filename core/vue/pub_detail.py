from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from core.models import Publication, Commentaire, like


@login_required
def pub_detail(request, pk):
    """
    Vue pour afficher le détail d'une publication (optionnelle)
    """
    publication = get_object_or_404(
        Publication.objects.select_related('auteur').prefetch_related(
            'Commentaires__auteur', 'likes'
        ), 
        pk=pk
    )
    
    publication.user_has_liked = publication.likes.filter(utilisateur=request.user).exists()
    publication.total_likes = publication.likes.count()
    
    context = {
        'publication': publication,
        'comment_form': CommentaireForm(),
    }
    
    return render(request, 'pub_detail.html', context)