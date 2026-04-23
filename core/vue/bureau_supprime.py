from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from core.models import Bureau
from core.forms import BureauForm


@login_required
def bureau_supprime(request, id):
    bureau = get_object_or_404(Bureau, id=id)
    
    if request.method == 'POST':
        nom_bureau = bureau.nom
        bureau.delete()
        messages.success(request, f"Le bureau {nom_bureau} a été supprimé!")
        return redirect('liste_bureaux')
    
    context = {'bureau': bureau}
    return render(request, 'bureau_supprimer.html', context)