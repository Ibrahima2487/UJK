from django.shortcuts import render, redirect
from core.forms import PublicationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models


def pub_create(request):
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.auteur = request.user
            form.save()
            return redirect('main')
    else:
        form = PublicationForm()
    
    return render(request, 'pub_create.html', {
        'form': form,
        'title': 'Créer une publication'
    })


""""

@login_required
def publication_create(request):
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.auteur = request.user
            publication.save()
            messages.success(request, 'Publication créée avec succès!')
            return redirect('publication_detail', pk=publication.pk)
    else:
        form = PublicationForm()
    
    return render(request, 'publications/publication_form.html', {
        'form': form,
        'title': 'Créer une publication'
    })

"""