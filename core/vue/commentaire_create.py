from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Count
from core.forms import CommentaireForm
from core.models import Publication, Commentaire
from django.views.decorators.http import require_POST

def commentaire_create (request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    form = CommentaireForm(request.POST)

    if form.is_valid():
        commentaire = form.save(commit=False)
        commentaire.auteur = request.user
        commentaire.publication = publication
        commentaire.save()
        return redirect("main")
    else:
        form = CommentaireForm()
    
    return render(request, 'commentaire_create.html', 
    {"form": form},
    )