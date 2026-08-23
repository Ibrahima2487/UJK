from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from core.models import Projet, Depense
from core.forms import ProjetForm


def projet_list(request):
    projets = Projet.objects.all().order_by('-date_debut')
    
    # Filtres
    search = request.GET.get('search')
    if search:
        projets = projets.filter(nom__icontains=search)
    
    statut = request.GET.get('statut')
    if statut:
        projets = projets.filter(statut=statut)
    
    # Pagination
    paginator = Paginator(projets, 10)
    page = request.GET.get('page')
    projets_page = paginator.get_page(page)
    
    context = {
        'projets': projets_page,
        'paginator': paginator,
        'page_obj': projets_page,
        'is_paginated': projets_page.has_other_pages(),
        'statut_choices': Projet.STATUT_CHOICES,
    }
    return render(request, 'projet_list.html', context)


def projet_detail(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    
    context = {
        'projet': projet,
    }
    return render(request, 'projet_detail.html', context)


def projet_ajoute(request):
    if request.method == "POST":
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('projet_list')
    else:
        form = ProjetForm()
    return render(request, 'projet_ajoute.html', {"form" : form})