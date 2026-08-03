from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Message
from core.forms import MessageForm  


@login_required
def message(request):
    """
    Vue unique pour afficher tous les messages et gérer l'ajout de nouveaux messages
    """
    
    tous_les_messages = Message.objects.all().order_by('date_envoi')
    
    # Gérer l'ajout de nouveau message
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            nouveau_message = form.save(commit=False)
            nouveau_message.envoyeur = request.user
            nouveau_message.save()
            
            # Supprimé les messages Django par défaut pour éviter la duplication
            return redirect('message')  # Rediriger pour éviter la resoumission du formulaire
        else:
            # Vous pouvez gérer les erreurs de formulaire ici si besoin
            pass
    else:
        form = MessageForm()
    
    context = {
        'messages': tous_les_messages,
        'form': form,
        'user': request.user
    }

    return render(request, 'message.html', context)