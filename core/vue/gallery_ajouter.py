from django.shortcuts import render, redirect
from core.forms import AlbumsForm
from django.db import models





def gallery_ajouter(request):
    if request.method == 'POST':
        form = AlbumsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_status')
    else:
        form = AlbumsForm()
    return render(request, 'gallery_ajouter.html', {'form': form})