from django.shortcuts import render, get_object_or_404
from core.models import Publication


def main_details(request, pk):
    pub = get_object_or_404(Publication, pk=pk)

    context = {
        'pub': pub,
    }
    return render(request, 'main_details.html', context)