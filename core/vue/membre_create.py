from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import login
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def membre_create(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        # Validation des données
        errors = []
        
        # Validation username
        if not username:
            errors.append('Le nom d\'utilisateur est requis')
        elif User.objects.filter(username=username).exists():
            errors.append('Ce nom d\'utilisateur existe déjà')  # CORRECTION ICI
        elif len(username) < 3:
            errors.append('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        
        # Validation email
        if not email:
            errors.append('L\'email est requis')
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors.append('Cet email est déjà utilisé')
            except ValidationError:
                errors.append('Email invalide')
        
        # Validation mot de passe
        if not password:
            errors.append('Le mot de passe est requis')
        elif len(password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères')
        elif not any(char.isdigit() for char in password):
            errors.append('Le mot de passe doit contenir au moins un chiffre')
        elif not any(char.isalpha() for char in password):
            errors.append('Le mot de passe doit contenir au moins une lettre')
        
        if password != confirm_password:
            errors.append('Les mots de passe ne correspondent pas')
        
        # Validation prénom et nom
        if not first_name:
            errors.append('Le prénom est requis')
        if not last_name:
            errors.append('Le nom est requis')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Création de l'utilisateur
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=is_active
                )
                
                # Gestion des permissions (optionnel)
                permissions = request.POST.getlist('permissions')
                if permissions:
                    user.user_permissions.set(permissions)
                
                # Gestion des groupes (optionnel)
                groups = request.POST.getlist('groups')
                if groups:
                    user.groups.set(groups)
                
               
                
                
                return redirect('membre_create')  
                
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création du compte: {str(e)}')
    
    # Préparation du contexte pour le template
    context = {
        'all_permissions': Permission.objects.all(),
        'all_groups': Group.objects.all(),
    }
    
    return render(request, 'membre_create.html', context)