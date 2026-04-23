from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from core.models import Utilisateur

def profile_qr(request, username):
    """
    Page publique accessible via QR code
    Affiche les informations essentielles du membre
    """
    # Récupérer l'utilisateur
    user = get_object_or_404(User, username=username)
    utilisateur = get_object_or_404(Utilisateur, user=user)
    
    context = {
        'utilisateur': utilisateur,
        'is_qr_access': True,  # Pour identifier que c'est un accès QR
    }
    
    return render(request, 'profile_qr.html', context)