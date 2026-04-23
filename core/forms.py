from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from core.models import actualite, albums, Utilisateur, Bureau, Publication, Commentaire, like, Contact, Payment
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


#Formulaire de Django
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        }) 
    )


#Formulaire de Actualité
class ActualiteForm(forms.ModelForm):
    class Meta:
        model = actualite
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenu'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }



#Formulaire de Albums
class AlbumsForm(forms.ModelForm):
    class Meta:
        model = albums
        fields = ['title', 'description', 'image', 'video', 'category']


#Formulaire de création de utilisateur
class UserForm(forms.ModelForm):
    """
    Formulaire pour modifier les informations de base de l'utilisateur.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
        }


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['texte']
        widgets = {
            'texte': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Écrivez votre commentaire...',
                'rows': 3,
                'id': 'comment-text-input'
            })
        }
        labels = {
            'texte': ''
        }

# ===== PARTIE LIKES ====== START
class likeForm(forms.ModelForm):
    class Meta:
        form = like
        fields = '__all__'

# LA partie profile des utilisateur
class ImageForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['image', 'numero', 'adresse']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'image': 'Choisir une image de profil'
        }
        labeels = {
            'numero' : 'Quel est votre numéro'
        }
        labeels = {
            'adresse' : 'Quel est votre adresse'
        }



# ======== Formulaire de contact ======
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["nom", "prenom", "adresse", "image", "email", "contenu"]



class BureauForm(forms.ModelForm):
    """Formulaire pour créer/modifier un bureau"""
    
    class Meta:
        model = Bureau
        fields = [
            'nom', 'sigle', 'type_bureau', 'mission',
            'zone_intervention', 'adresse_locale', 'bureau_parent',
            'president', 'vice_president', 'secretaire', 'secretaire_adjoint',
            'tresorier', 'responsable_technique', 'animateur_communautaire',
            'membres_actifs', 'benevoles',
            'date_creation', 'frequence_reunions',
            'telephone_contact', 'email_contact', 'statut'
        ]
        
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Comité Éducation de Kakony Centre'
            }),
            'sigle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CEKC',
                'maxlength': 15
            }),
            'type_bureau': forms.Select(attrs={'class': 'form-select'}),
            'mission': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez la mission et les objectifs du bureau/comité...'
            }),
            'zone_intervention': forms.Select(attrs={'class': 'form-select'}),
            'adresse_locale': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Près de la mosquée centrale'
            }),
            'bureau_parent': forms.Select(attrs={'class': 'form-select'}),
            'president': forms.Select(attrs={'class': 'form-select'}),
            'vice_president': forms.Select(attrs={'class': 'form-select'}),
            'secretaire': forms.Select(attrs={'class': 'form-select'}),
            'secretaire_adjoint': forms.Select(attrs={'class': 'form-select'}),
            'tresorier': forms.Select(attrs={'class': 'form-select'}),
            'responsable_technique': forms.Select(attrs={'class': 'form-select'}),
            'animateur_communautaire': forms.Select(attrs={'class': 'form-select'}),
            'membres_actifs': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'benevoles': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'date_creation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'frequence_reunions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Mensuelle'
            }),
            'telephone_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XXX XXX'
            }),
            'email_contact': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Utilisateurs actifs pour les postes
        users_actifs = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        user_fields = [
            'president', 'vice_president', 'secretaire', 'secretaire_adjoint',
            'tresorier', 'responsable_technique', 'animateur_communautaire'
        ]
        
        for field_name in user_fields:
            self.fields[field_name].queryset = users_actifs
        
        self.fields['membres_actifs'].queryset = users_actifs
        self.fields['benevoles'].queryset = users_actifs
        
        # Bureaux parents possibles
        if self.instance and self.instance.pk:
            self.fields['bureau_parent'].queryset = Bureau.objects.exclude(
                pk=self.instance.pk
            ).filter(statut='ACTIF')
        else:
            self.fields['bureau_parent'].queryset = Bureau.objects.filter(statut='ACTIF')
    
    def clean_sigle(self):
        """Validation du sigle"""
        sigle = self.cleaned_data['sigle'].upper()
        
        queryset = Bureau.objects.filter(sigle=sigle)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError(f"Le sigle '{sigle}' est déjà utilisé.")
        
        return sigle
    
    def clean(self):
        """Validation croisée"""
        cleaned_data = super().clean()
        
        # Vérifier les postes dirigeants
        dirigeants = [
            cleaned_data.get('president'),
            cleaned_data.get('vice_president'),
            cleaned_data.get('secretaire'),
            cleaned_data.get('secretaire_adjoint'),
            cleaned_data.get('tresorier'),
            cleaned_data.get('responsable_technique'),
            cleaned_data.get('animateur_communautaire')
        ]
        
        dirigeants_valides = [d for d in dirigeants if d is not None]
        
        if len(set(dirigeants_valides)) != len(dirigeants_valides):
            raise ValidationError(
                "Une personne ne peut pas occuper plusieurs postes dirigeants."
            )
        
        # Validation hiérarchique
        bureau_parent = cleaned_data.get('bureau_parent')
        type_bureau = cleaned_data.get('type_bureau')
        
        if type_bureau == 'PRINCIPAL' and bureau_parent:
            raise ValidationError(
                "Un bureau principal ne peut pas avoir de structure de rattachement."
            )
        
        return cleaned_data


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titre', 'contenu', 'image', 'video']
    


# Partie comptable

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'


from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """Formulaire pour envoyer un message"""
    
    class Meta:
        model = Message
        fields = ['contenu', 'fichier']
        
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Écrivez votre message...',
                'rows': 3
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            })
        }
        
        labels = {
            'contenu': 'Message',
            'fichier': 'Fichier (optionnel)'
        }    

        

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        }),
        min_length=8
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data