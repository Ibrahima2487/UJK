from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.forms import PublicationForm
from core.models import Publication


def pub_modifie(request, pk):
    pubs = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        pubs = PublicationForm(request.POST, instance=pubs)
        if form.is_valid():
            form.save()
            return redirect('main')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous." )
    else:
        form = PublicationForm(instance=pubs)

    context = {
        'form' : form,
        'pubs' : pubs
    }
    return render(request, 'pub_modifie.html', context)