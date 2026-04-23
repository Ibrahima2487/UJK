from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from core.forms import MessageForm


@login_required
def message_create(request):
    """Ajouter un nouveau message"""
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            nouveau_message = form.save(commit=False)
            nouveau_message.envoyeur = request.user
            nouveau_message.save()
            django_messages.success(request, "Message envoyé !")
        else:
            django_messages.error(request, "Erreur dans le formulaire")
    
    return redirect('message')