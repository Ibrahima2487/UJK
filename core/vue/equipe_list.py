from django.shortcuts import render
from core.models import Utilisateur

def equipe_list(request):
    utilisateurs = Utilisateur.objects.select_related('user').all()
    return render(request, 'equipe_list.html', {'utilisateurs': utilisateurs})