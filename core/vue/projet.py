from django.shortcuts import render, redirect, get_object_or_404
from core.models import Projet
from core.forms import ProjetForm


def projet_list(request):
    projets = Projet.objects.all()

    context = {
        'projets' : projets
    }
    return render(request, 'projet_list.html', context)

def projet_ajoute(request):
    if request.method == "POST":
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('projet_list')
    else:
        form = ProjetForm()
    return render(request, 'projet_ajoute.html', {"form" : form})