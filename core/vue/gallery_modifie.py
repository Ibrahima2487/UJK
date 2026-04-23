from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.models import albums
from core.forms import AlbumsForm



# Modifier un album

def gallery_modifie(request, pk):
    """Modifier un album existant"""
    album = get_object_or_404(albums, pk=pk)
    
    if request.method == 'POST':
        form = AlbumsForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, f'L\'album "{album.title}" a été modifié avec succès.')
            return redirect('gallery_status')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = AlbumsForm(instance=album)

    return render(request, 'gallery_modifie.html', {
        'form': form,
        'album': album,
        'title': 'Modifier l\'album'
    })
