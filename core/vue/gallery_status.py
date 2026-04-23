# views.py - Gestion des Albums
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.models import albums

@login_required
def gallery_status(request):
    """Vue principale pour afficher tous les albums"""
    # Filtrage par catégorie si demandé
    category_filter = request.GET.get('category')
    albums_list = albums.objects.all().order_by('-date_created')
    
    if category_filter:
        albums_list = albums_list.filter(category=category_filter)
    
    # Pagination
    paginator = Paginator(albums_list, 12)  # 12 albums par page
    page_number = request.GET.get('page')
    albums_page = paginator.get_page(page_number)
    
    # Statistiques par catégorie
    categories_stats = {}
    for choice_value, choice_label in albums.CATEGORY_CHOICES:
        count = albums.objects.filter(category=choice_value).count()
        categories_stats[choice_value] = {
            'label': choice_label,
            'count': count
        }
    
    context = {
        'albums': albums_page,
        'categories': albums.CATEGORY_CHOICES,
        'categories_stats': categories_stats,
        'current_category': category_filter,
        'total_albums': albums.objects.count(),
        'title': 'Gestion de la gallerie'
    }
    return render(request, 'gallery_status.html', context)

"""

@login_required
def ajouter_album(request):
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        
        if title:
            nouvel_album = albums.objects.create(
                title=title,
                description=description,
                category=category,
                image=image,
                video=video
            )
            messages.success(request, f'Album "{title}" ajouté avec succès!')
            return redirect('gestion_albums')
        else:
            messages.error(request, 'Le titre est obligatoire.')
    
    context = {
        'categories': albums.CATEGORY_CHOICES,
        'title': 'Ajouter un album'
    }
    return render(request, 'ajouter_album.html', context)

@login_required
def modifier_album(request, pk):
    
    album = get_object_or_404(albums, pk=pk)
    
    if request.method == 'POST':
        album.title = request.POST.get('title', album.title)
        album.description = request.POST.get('description', album.description)
        album.category = request.POST.get('category', album.category)
        
        if 'image' in request.FILES:
            # Supprimer l'ancienne image si une nouvelle est uploadée
            if album.image:
                try:
                    album.image.delete()
                except:
                    pass
            album.image = request.FILES['image']
        
        if 'video' in request.FILES:
            # Supprimer l'ancienne vidéo si une nouvelle est uploadée
            if album.video:
                try:
                    album.video.delete()
                except:
                    pass
            album.video = request.FILES['video']
        
        album.save()
        messages.success(request, f'Album "{album.title}" modifié avec succès!')
        return redirect('gestion_albums')
    
    context = {
        'album': album,
        'categories': albums.CATEGORY_CHOICES,
        'title': f'Modifier l\'album: {album.title}'
    }
    return render(request, 'modifier_album.html', context)

@login_required
@require_http_methods(["POST"])
def supprimer_album(request, pk):
    
    album = get_object_or_404(albums, pk=pk)
    
    # Supprimer les fichiers du serveur
    if album.image:
        try:
            album.image.delete()
        except:
            pass
    
    if album.video:
        try:
            album.video.delete()
        except:
            pass
    
    title = album.title
    album.delete()
    messages.success(request, f'Album "{title}" supprimé avec succès!')
    return redirect('gestion_albums')

"""