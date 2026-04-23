from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from core.models import albums

def gallery_supprime(request, pk):
    """Supprimer un album"""
    album = get_object_or_404(albums, pk=pk)
    
    if request.method == 'POST':
        album_title = album.title
        album.delete()
        messages.success(request, f'L\'album "{album_title}" a été supprimé avec succès.')
        return redirect('gallerie_status')

    return render(request, 'gallery_supprime.html', {'album': album})