from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from core.models import Bureau
from core.forms import BureauForm

@login_required
def bureau_modifie(request, pk):  # Changement de 'id' à 'pk'
    bureau = get_object_or_404(Bureau, pk=pk)  # Utilisation de pk
    
    if request.method == 'POST':
        form = BureauForm(request.POST, instance=bureau)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les modifications du bureau {bureau.nom} ont été enregistrées!")
            return redirect('bureau_details', pk=bureau.pk)  # Redirection vers les détails du bureau
    else:
        form = BureauForm(instance=bureau)
    
    context = {
        'form': form,
        'bureau': bureau,
    }
    return render(request, 'bureau_modifie.html', context)