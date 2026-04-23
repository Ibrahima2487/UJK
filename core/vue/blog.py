from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.models import actualite
from core.forms import ActualiteForm 



def blog(request):
    actualites = actualite.objects.all().order_by('-date_created')  # On récupère les actualités
    context = {
        'actualites': actualites,  # On envoie les actualités au template
    }
    return render(request, 'blog.html', context)




# ======== BLOG STATUS ================

@login_required
def blog_status(request):
    """Vue principale pour afficher toutes les actualités avec pagination"""
    # Récupérer toutes les actualités ordonnées par date de création
    actualites_list = actualite.objects.all().order_by('-date_created')
    
    # Configurer la pagination - 10 articles par page
    paginator = Paginator(actualites_list, 10)
    page = request.GET.get('page')  # Récupérer le numéro de page depuis l'URL
    
    try:
        actualites = paginator.page(page)
    except PageNotAnInteger:
        # Si le paramètre page n'est pas un entier, afficher la première page
        actualites = paginator.page(1)
    except EmptyPage:
        # Si la page demandée est hors limite, afficher la dernière page
        actualites = paginator.page(paginator.num_pages)
    
    context = {
        'actualites': actualites,
        'title': 'Gestion des Actualités'
    }
    return render(request, 'blog_status.html', context)



# ================= BLOG CREATE =========
def blog_create(request):
    if request.method == 'POST':
        form = ActualiteForm(request.POST, request.FILES)  # request.FILES pour les images !
        if form.is_valid():
            form.save()
            return redirect('blog_status')  
    else:
        form = ActualiteForm()

    return render(request, 'blog_create.html', {'form': form})


# =========== BLOG MODIFIE ========================


@login_required
def blog_modifie(request, pk):
    """Vue pour modifier une actualité existante"""
    actu = get_object_or_404(actualite, pk=pk)
    
    if request.method == 'POST':
        actu.title = request.POST.get('title', actu.title)
        actu.contenu = request.POST.get('contenu', actu.contenu)
        
        if 'image' in request.FILES:
            actu.image = request.FILES['image']
        
        actu.save()
        messages.success(request, 'Actualité modifiée avec succès!')
        return redirect('blog_status')
    
    context = {
        'actualite': actu,
        'title': 'Modifier l\'actualité'
    }
    return render(request, 'blog_modifie.html', context)



# Version alternative avec page de confirmation
@login_required
def blog_supprime(request, pk):
    """Vue pour afficher la page de confirmation de suppression"""
    actualite_obj = get_object_or_404(actualite, pk=pk)
    
    if request.method == 'POST':
        # Supprimer l'image du serveur si elle existe
        if actualite_obj.image:
            try:
                actualite_obj.image.delete()
            except:
                pass
        
        title = actualite_obj.title
        actualite_obj.delete()
        messages.success(request, f'Actualité "{title}" supprimée avec succès!')
        return redirect('blog_status')
    
    context = {
        'actualite': actualite_obj,
        'title': 'Confirmer la suppression'
    }
    return render(request, 'blog_supprime.html', context)