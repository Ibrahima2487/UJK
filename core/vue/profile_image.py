from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from core.models import Utilisateur
from core.forms import ImageForm

@login_required
def profile_image(request):
    # Vérifier si l'utilisateur a déjà un profil Utilisateur
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        is_new_profile = False
    except Utilisateur.DoesNotExist:
        # Créer un nouveau profil Utilisateur pour l'user connecté
        utilisateur = Utilisateur.objects.create(user=request.user)
        is_new_profile = True
        messages.info(request, 'Votre profil a été créé. Vous pouvez maintenant ajouter une image.')

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, ' Votre image de profil a été mise à jour avec succès !')
            return redirect('profile')
        else:
            messages.error(request, ' Veuillez corriger les erreurs ci-dessous.')
    else:
        form = ImageForm(instance=utilisateur)
    
    # Vérifier si l'utilisateur a une image personnalisée
    has_custom_image = utilisateur.image and utilisateur.image.name != 'profiles/default.png'
    
    
    
    return render(request, 'profile_image.html', {"form" : form})
