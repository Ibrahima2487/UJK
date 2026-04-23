from django.shortcuts import render
from core.models import Commentaire

def comme_details (request, pk):
    commentaires = get_object_or_404(Commentaire, pk=pk)
    context = {
        'comment' : comment
    }
    return render(request, 'comme_details.html', context)