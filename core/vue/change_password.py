from django.shortcuts import render, get_object_or_404, redirect
from core.forms import ChangePasswordForm
from django.contrib.auth.models import User

def change_password(request, user_id):
    # Récupérer l'utilisateur par son ID
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            # Changer le mot de passe
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            return redirect('success_page')  # Rediriger vers une page de succès
    else:
        form = ChangePasswordForm()
    
    return render(request, 'change_password.html', {
        'form': form,
        'user': user
    })