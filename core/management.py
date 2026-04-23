from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.dispatch import receiver
import os

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    """
    Crée automatiquement un superuser si aucun utilisateur n'existe.
    """
    if sender.name == 'core':  # S'exécute seulement après la migration de l'app core
        User = get_user_model()
        
        # Vérifier si un superuser existe déjà
        if not User.objects.filter(is_superuser=True).exists():
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'udjk')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@udjk.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'udjk123')
            
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superuser '{username}' créé avec succès!")
        else:
            print("ℹ️  Un superuser existe déjà.")