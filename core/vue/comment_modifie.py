from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.forms import PublicationForm
from core.models import Publication


def comment_modifie(request, pk):
    comment = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('main')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous." )
    else:
        form = PublicationForm(instance=comment)

    context = {
        'form' : form,
        'comment' : comment
    }
    return render(request, 'comment_modifie.html', context)