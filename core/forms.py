from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from core.models import actualite, albums, Utilisateur, Bureau, Publication, Commentaire, like, Contact, Payment, Temoin
from core.models import MessageBureau, Affectation, Caisse, Payment, Depense, JournalCaisse, FicheControle
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


# ============== TEMOIGNAGE ==========
class TemoinForm(forms.ModelForm):
    class Meta:
        model = Temoin
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'prenom' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prenom'}),
            'genre' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Votre genre'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message'}),
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
    
    
    class Meta:
        model = Bureau
        fields = "__all__"


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


# =========== TEMOIN ========= START
class TemoinForm(forms.ModelForm):
    class Meta:
        model = Temoin
        fields = "__all__"


# ============ BUREAU ========= SATRT
class BureauForm(forms.ModelForm):
    class Meta:
        model = Bureau
        fields = "__all__"


# ========== AFFECTATION ===== START
class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = "__all__"

# ========= MESSAGE BUREAU ===== START
class MessageBureauForm(forms.ModelForm):
    class Meta:
        model = MessageBureau
        fields = "__all__"




#=============== COMPTABLITÉ ==========

#=== CAISSE
class CaisseForm(forms.ModelForm):
    class Meta:
        model = Caisse
        fields = "__all__"

#===== DEPENSE ========
class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = "__all__"

#===== JOURNALCAISSE =====
class JournalCaisseForm(forms.ModelForm):
    class Meta:
        model = JournalCaisse
        fields = "__all__"


# ===== FICHECONTROLE 
class FicheControleForm(forms.ModelForm):
    class Meta:
        model = FicheControle
        fields = "__all__"