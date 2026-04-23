from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from core.models import Bureau
from core.forms import BureauForm



@login_required
def bureau_ajouter(request):
    if request.method == 'POST':
        form = BureauForm(request.POST)
        if form.is_valid():
            nouveau_bureau = form.save()
            messages.success(request, f"Le bureau {nouveau_bureau.nom} a été créé avec succès!")
            return redirect('bureau')
    else:
        form = BureauForm()
    
    context = {'form': form}
    return render(request, 'bureau_ajouter.html', context)
