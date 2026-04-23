from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.models import Publication, Commentaire, like
from core.forms import CommentaireForm, PublicationForm

@login_required
def ajouter_commentaire_modal(request, publication_id):
    """Ajoute un commentaire via modal (AJAX)"""
    publication = get_object_or_404(Publication, id=publication_id)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.publication = publication
            commentaire.auteur = request.user
            commentaire.save()
            
            # Retourner une réponse JSON pour mise à jour AJAX
            return JsonResponse({
                'success': True,
                'message': 'Commentaire ajouté avec succès!',
                'comment_html': render_to_string('main.html', {
                    'commentaire': commentaire
                })
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
def modifier_commentaire_modal(request, commentaire_id):
    """Modifie un commentaire via modal"""
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, auteur=request.user)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST, instance=commentaire)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Commentaire modifié avec succès!',
                'texte': commentaire.texte
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    # Retourner le formulaire pour l'édition
    form = CommentaireForm(instance=commentaire)
    form_html = render_to_string('commentaire_form.html', {
        'form': form,
        'publication': commentaire.publication,
        'is_edit': True,
        'commentaire_id': commentaire.id
    })
    
    return JsonResponse({
        'success': True,
        'form_html': form_html
    })

@login_required
def supprimer_commentaire_modal(request, commentaire_id):
    """Supprime un commentaire via modal"""
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, auteur=request.user)
    
    if request.method == 'POST':
        publication_id = commentaire.publication.id
        commentaire.delete()
        return JsonResponse({
            'success': True,
            'message': 'Commentaire supprimé avec succès!',
            'publication_id': publication_id
        })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def get_commentaire_form(request, publication_id):
    """Retourne le formulaire de commentaire pour le modal"""
    publication = get_object_or_404(Publication, id=publication_id)
    form = CommentaireForm()
    
    form_html = render_to_string('partials/commentaire_form.html', {
        'form': form,
        'publication': publication,
        'is_edit': False
    })
    
    return JsonResponse({'form_html': form_html})

def liste_commentaires(request, publication_id):
    """Retourne la liste des commentaires d'une publication"""
    publication = get_object_or_404(Publication, id=publication_id)
    commentaires = Commentaire.objects.filter(publication=publication).order_by('date_com')
    
    commentaires_html = render_to_string('partials/commentaires_list.html', {
        'commentaires': commentaires,
        'publication': publication
    })
    
    return JsonResponse({'commentaires_html': commentaires_html})

# Vues pour les publications (optionnel)
    