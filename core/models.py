from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator #valideurs pour les champs
from django.utils.text import slugify 
from django.utils import timezone
import os
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime, timedelta
import json
import uuid
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files import File
from django.conf import settings
import qrcode

# ========= UTILISATEUR ======== 
class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numero = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='profiles/')
    adresse = models.CharField(max_length=100, default="Kakony")
    #en_ligne = models.BooleanField(default=False)
    badge_png = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def marquer_en_ligne(self):
        self.en_ligne = True
        self.derniere_activite = timezone.now()
        self.save()

    def marquer_hors_ligne(self):
        self.en_ligne = False
        self.save()

    

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Sauvegarde initiale pour avoir un ID
        super().save(*args, **kwargs)
        
        # Redimensionner l'image de profil
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)
        
        # Générer le badge
        self.generer_badge()
        
        # Sauvegarder à nouveau pour enregistrer le badge
        super().save(*args, **kwargs)
    
    def generer_badge(self):
    # Design minimaliste futuriste
        badge = Image.new("RGB", (500, 600), "#2c3e50")
        draw = ImageDraw.Draw(badge)
    
        width, height = 500, 600
        center_x, center_y = width // 2, height // 2

    # Grand cercle central avec gradient
        for r in range(200, 0, -2):
            alpha = int(255 * (r / 200))
            color = (242, 130, 65, alpha)
            draw.ellipse([center_x-r, center_y-r, center_x+r, center_y+r], 
                    outline=(242, 130, 65), width=2)
    
    # Grille de triangles
            triangle_size = 40
        for x in range(0, width, triangle_size):
             for y in range(0, height, triangle_size):
                if (x // triangle_size + y // triangle_size) % 2 == 0:
                    points = [(x, y), (x+triangle_size, y), (x, y+triangle_size)]
                    draw.polygon(points, outline="#F28241", width=1)
    
    # Lignes de connexion diagonales
        for i in range(0, width + height, 20):
            draw.line([(i, 0), (0, i)], fill="#F28241", width=1)
            draw.line([(width-i, height), (width, height-i)], fill="#F28241", width=1)
    
            return badge

        

        # Ajouter le logo
        try:
            logo_path = f"{settings.BASE_DIR}/media/profiles/logo.png"
            logo = Image.open(logo_path).resize((250, 250))
            badge.paste(logo, (10, 50))
        except:
            pass
    
        # Ajouter l'image de l'utilisateur
        if self.image:
            try:
                user_image = Image.open(self.image.path).resize((200, 250))
                badge.paste(user_image, (10, 10))
                
            except:
                pass

        
        # Ajouter le texte
        try:
            # Essayer de charger une police, sinon utiliser la police par défaut
            font_path = f"{settings.BASE_DIR}/static/fonts/arial.ttf"
            font = ImageFont.truetype(font_path, 26)
        except:
            font = ImageFont.load_default()
        
        # Ajouter le nom d'utilisateur
        draw.text((10, 350), f" Membre de UJK\n Nom : {self.user.get_full_name() or self.user.username}", fill="white", font=font)
        
       

        # Générer et ajouter le QR code
        qr_data = f"{settings.SITE_URL}/udjkplatform/profiles/{self.id}/"
        qr_img = qrcode.make(qr_data)
        qr_img = qr_img.resize((250, 250))
        badge.paste(qr_img, (200, 200))

        # Sauvegarder le badge
        buffer = BytesIO()
        badge.save(buffer, format="PNG")
        file_png = File(buffer, name=f"Badge_{self.id}.png")
        
        # Sauvegarder le badge dans le champ badge_png
        self.badge_png.save(file_png.name, file_png, save=False)
  


# ========= ACTUALITÉ ==========
class actualite(models.Model):
    CHOICE_CATEGORIE = [
        ('éducation', 'Éducation'),
        ('santé', 'Santé'),
        ('environement', 'Énvironement'),
        ('culturel', 'Culturel'),
        
    ]
    title = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='static/blog/', blank=True, null=True)
    categorie = models.CharField(max_length=250, choices=CHOICE_CATEGORIE, default='Éducatif')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Temoin (models.Model):
    GENRE_TEMOIN = [
        ('M', 'm'),
        ('F', 'f'),
    ]
    nom = models.CharField(max_length=100, null=True)
    prenom = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='temoin', blank=True, null=True)
    genre = models.CharField(max_length=50, choices=GENRE_TEMOIN, default='M')
    contenue = models.TextField()
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return f" {self.nom} - {self.prenom} - {self.genre}"





# ========== ALBUMS ===========
class albums(models.Model):  
    CATEGORY_CHOICES = [   # liste de categorie
        ('evenement', 'Événement'),
        ('projet', 'Projet'),
        ('video', 'Vidéo'),
        ('reunion', 'Réunion'),
        ('autre', 'Autre'),
        ('formation', 'Formation'),
        ('conference', 'Conférence'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='static/albums/images/', blank=True, null=True)  # <-- évite de mettre "static/"
    date_created = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='static/albums/videos/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='evenement')

    def __str__(self):
        return self.title


# ========== BUREAU ===========
class Bureau(models.Model):
    
    
    TYPE_BUREAU_CHOICES = [
        ('PRINCIPAL', 'Bureau Principal'),
        ('EDUCATION', 'Comité Éducation & Formation'),
        ('SANTE', 'Comité Santé & Hygiène'),
        ('JEUNESSE', 'Comité Jeunesse & Sport'),
        ('FEMMES', 'Comité des Femmes'),
        ('ENVIRONNEMENT', 'Comité Environnement'),
        ('CULTURE', 'Comité Culture & Tradition'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('EN_PROJET', 'En Projet'),
        ('SUSPENDU', 'Suspendu'),
    ]

    ZONE_INTERVENTION_CHOICES = [
        ('KAKONY_CENTRE', 'Kakony Centre'),
        ('Village', 'Village'),
        
    ]

    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom du bureau", help_text="Nom complet du bureau que vous voullez créez")
    sigle = models.CharField(max_length=15, unique=True, verbose_name="Sigle", help_text="Code unique (ex: BPK, CEK, CSK, CAK)")
    type_bureau = models.CharField(max_length=20, choices=TYPE_BUREAU_CHOICES, default='UDJK', verbose_name="Type de structure")
    mission = models.TextField(verbose_name="Mission et objectifs", help_text="Description de la mission et des objectifs du bureau/comité")
    
    # Localisation spécifique à Kakony
    zone_intervention = models.CharField(
        max_length=30,
        choices=ZONE_INTERVENTION_CHOICES,
        default='ENSEMBLE_COMMUNE',
        verbose_name="Zone d'intervention"
    )
    
    adresse_locale = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Adresse locale",
        help_text="Lieu précis à Kakony"
    )
    
    # Structure hiérarchique
    bureau_parent = models.ForeignKey(
        "self", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name="structures_filiales",
        verbose_name="Structure de rattachement"
    )
    
    # Membres dirigeants
    president = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name="bureaux_presides_kakony",
        verbose_name="Président(e)"
    )
    
    vice_president = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bureaux_vice_president_kakony",
        verbose_name="Vice-président(e)",
        null=True,
        blank=True
    )
    
    secretaire = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name="bureaux_secretaire_kakony",
        verbose_name="Secrétaire"
    )
    
    tresorier = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name="bureaux_tresorier_kakony",
        verbose_name="Trésorier(ère)"
    )
    
    # Responsables techniques (selon le type de comité)
    responsable_technique = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bureaux_technique_kakony",
        verbose_name="Responsable Technique",
        null=True,
        blank=True,
        help_text="Expert ou technicien spécialisé dans le domaine"
    )
    
    animateur_communautaire = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bureaux_animateur_kakony",
        verbose_name="Animateur Communautaire",
        null=True,
        blank=True,
        help_text="Personne chargée de la mobilisation communautaire"
    )
    
    # Membres actifs
    membres_actifs = models.ManyToManyField(
        User,
        blank=True,
        related_name="bureaux_membre_actif_kakony",
        verbose_name="Membres actifs",
        help_text="Membres participant régulièrement aux activités"
    )
    
    # Bénévoles et sympathisants
    benevoles = models.ManyToManyField(
        User,
        blank=True,
        related_name="bureaux_benevole_kakony",
        verbose_name="Bénévoles"
    )
    
    # Informations sur la constitution
    date_creation = models.DateField(
        verbose_name="Date de création",
        help_text="Date de création du bureau/comité"
    )
    
    date_derniere_assemblee = models.DateField(
        null=True,
        blank=True,
        verbose_name="Dernière assemblée",
        help_text="Date de la dernière assemblée générale"
    )
    
    frequence_reunions = models.CharField(
        max_length=50,
        default='Mensuelle',
        verbose_name="Fréquence des réunions",
        help_text="Ex: Hebdomadaire, Mensuelle, Trimestrielle"
    )
    
    # Métadonnées
    
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='ACTIF',
        verbose_name="Statut"
    )
    
    niveau_hierarchique = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Niveau hiérarchique"
    )
    # Contacts et communication
    telephone_contact = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone de contact"
    )
    
    email_contact = models.EmailField(
        blank=True,
        verbose_name="Email de contact"
    )
    taux_reussite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taux de réussite (%)",
        help_text="Pourcentage de projets menés à bien"
    )


    class Meta:
        verbose_name = "Bureau"
        verbose_name_plural = "Bureaux"
        ordering = ['niveau_hierarchique', 'type_bureau', 'nom']
        unique_together = [['nom', 'zone_intervention']]
        permissions = [
            ("export_bureaux", "Peut exporter les données des bureaux"),
            ("gerer_tous_bureaux", "Peut gérer tous les bureaux sans restriction"),
        ]

    def __str__(self):
        return f"{self.nom} - {self.get_zone_intervention_display()}"

    def clean(self):
        """Validation personnalisée du modèle"""
        super().clean()
        
        # Récupérer tous les membres dirigeants
        membres_dirigeants = [
            self.president,
            self.secretaire,
            self.tresorier,
        ]
        
        # Ajouter les postes optionnels
        if self.vice_president:
            membres_dirigeants.append(self.vice_president)
        
        if self.responsable_technique:
            membres_dirigeants.append(self.responsable_technique)
        if self.animateur_communautaire:
            membres_dirigeants.append(self.animateur_communautaire)
        
        # Vérifier l'unicité
        if len(set(membres_dirigeants)) != len(membres_dirigeants):
            raise ValidationError(
                "Une personne ne peut pas occuper plusieurs postes dirigeants dans le même bureau"
            )
        
        # Validation hiérarchique
        if self.bureau_parent:
            current = self.bureau_parent
            while current:
                if current == self:
                    raise ValidationError("Un bureau ne peut pas être son propre parent")
                current = current.bureau_parent

    def save(self, *args, **kwargs):
        """Calcule le niveau hiérarchique et met à jour les statistiques"""
        if self.bureau_parent:
            self.niveau_hierarchique = self.bureau_parent.niveau_hierarchique + 1
        else:
            self.niveau_hierarchique = 0
            
        super().save(*args, **kwargs)

    # Propriétés et méthodes utilitaires
    @property
    def est_bureau_principal(self):
        """Vérifie si c'est le bureau principal"""
        return self.type_bureau == 'PRINCIPAL'

    @property
    def adresse_complete_kakony(self):
        """Retourne l'adresse complète dans Kakony"""
        adresse = f"{self.get_zone_intervention_display()}, Kakony"
        if self.adresse_locale:
            adresse = f"{self.adresse_locale}, {adresse}"
        return f"{adresse}, Sous-Préfecture de Gaoual, Préfecture de Gaoual, Région de Boké, Guinée"

    def get_membres_dirigeants(self):
        """Retourne tous les membres dirigeants avec leurs postes"""
        dirigeants = [
            ('Président(e)', self.president),
            ('Secrétaire', self.secretaire),
            ('Trésorier(ère)', self.tresorier),
        ]
        
        # Ajouter les postes optionnels
        if self.vice_president:
            dirigeants.insert(1, ('Vice-président(e)', self.vice_president))
        if self.secretaire_adjoint:
            dirigeants.append(('Secrétaire Adjoint(e)', self.secretaire_adjoint))
        if self.responsable_technique:
            dirigeants.append(('Responsable Technique', self.responsable_technique))
        if self.animateur_communautaire:
            dirigeants.append(('Animateur Communautaire', self.animateur_communautaire))
        
        return dirigeants

    def get_tous_les_membres(self):
        """Retourne tous les membres (dirigeants + actifs + bénévoles)"""
        dirigeants = [membre for _, membre in self.get_membres_dirigeants()]
        membres_actifs = list(self.membres_actifs.all())
        benevoles = list(self.benevoles.all())
        
        # Éliminer les doublons
        tous_membres = list(set(dirigeants + membres_actifs + benevoles))
        return tous_membres

    def get_effectif_total(self):
        """Retourne l'effectif total du bureau/comité"""
        return len(self.get_tous_les_membres())

    def get_impact_total(self):
        """Calcule l'impact total (bénéficiaires directs + indirects)"""
        return self.nombre_beneficiaires_directs + self.nombre_beneficiaires_indirects

    # Méthodes de contrôle d'accès
    def is_president(self, user):
        """Vérifie si l'utilisateur est président"""
        return self.president == user

    def is_membre_dirigeant(self, user):
        """Vérifie si l'utilisateur fait partie de l'équipe dirigeante"""
        dirigeants = [membre for _, membre in self.get_membres_dirigeants()]
        return user in dirigeants

    def is_membre_actif(self, user):
        """Vérifie si l'utilisateur est membre actif"""
        return (self.is_membre_dirigeant(user) or 
                self.membres_actifs.filter(id=user.id).exists() or
                self.benevoles.filter(id=user.id).exists())

    def peut_modifier(self, user):
        """Vérifie si l'utilisateur peut modifier les informations"""
        if self.is_president(user):
            return True
        if self.bureau_parent and self.bureau_parent.is_president(user):
            return True
        return False

    # Méthodes pour la structure organisationnelle
    def get_chemin_organisationnel(self):
        """Retourne le chemin organisationnel complet"""
        chemin = []
        bureau_actuel = self
        while bureau_actuel:
            chemin.insert(0, bureau_actuel.nom)
            bureau_actuel = bureau_actuel.bureau_parent
        return " → ".join(chemin)

    def get_structures_filiales_actives(self):
        """Retourne les structures filiales actives"""
        return self.structures_filiales.filter(statut='ACTIF')

    def get_tous_les_descendants(self):
        """Retourne tous les descendants dans la hiérarchie"""
        descendants = []
        for filiale in self.get_structures_filiales_actives():
            descendants.append(filiale)
            descendants.extend(filiale.get_tous_les_descendants())
        return descendants

    # Méthodes de suivi et évaluation
    def calculer_taux_reussite(self):
        """Calcule automatiquement le taux de réussite"""
        total_projets = self.projets_realises + self.projets_en_cours
        if total_projets > 0:
            self.taux_reussite = (self.projets_realises / total_projets) * 100
            self.save(update_fields=['taux_reussite'])

    

    def get_impact_consolide(self):
        """Calcule l'impact consolidé avec les structures filiales"""
        impact = {
            'beneficiaires_directs': self.nombre_beneficiaires_directs,
            'beneficiaires_indirects': self.nombre_beneficiaires_indirects,
            'projets_realises': self.projets_realises,
            'projets_en_cours': self.projets_en_cours,
        }
        
        for filiale in self.get_structures_filiales_actives():
            impact_filiale = filiale.get_impact_consolide()
            for cle, valeur in impact_filiale.items():
                impact[cle] += valeur
        
        return impact

    def generer_rapport_communautaire(self):
        """Génère un rapport d'activité communautaire"""
        impact = self.get_impact_consolide()
        
        return {
            'structure': self.nom,
            'type': self.get_type_bureau_display(),
            'zone': self.get_zone_intervention_display(),
            'president': str(self.president),
            'effectif': self.get_effectif_total(),
            'beneficiaires_directs': impact['beneficiaires_directs'],
            'beneficiaires_indirects': impact['beneficiaires_indirects'],
            'impact_total': impact['beneficiaires_directs'] + impact['beneficiaires_indirects'],
            'projets_realises': impact['projets_realises'],
            'projets_en_cours': impact['projets_en_cours'],
            
            'taux_reussite': self.taux_reussite,
            'statut': self.get_statut_display(),
            'derniere_assemblee': self.date_derniere_assemblee,
            'partenaires': {
                'locaux': self.partenaires_locaux,
                'externes': self.partenaires_externes,
            },
            'contact': {
                'telephone': self.telephone_contact,
                'email': self.email_contact,
            }
        }

    # Méthodes d'analyse et recommandations
    def get_recommandations_amelioration(self):
        """Suggère des améliorations basées sur les indicateurs"""
        recommandations = []
        
        if self.taux_reussite and self.taux_reussite < 70:
            recommandations.append("Améliorer le suivi des projets pour augmenter le taux de réussite")
        
        if self.get_effectif_total() < 5:
            recommandations.append("Recruter plus de membres actifs pour renforcer les capacités")
        
        if not self.date_derniere_assemblee or (timezone.now().date() - self.date_derniere_assemblee).days > 90:
            recommandations.append("Organiser une assemblée générale pour dynamiser les activités")
        
        
        
        if not self.partenaires_externes:
            recommandations.append("Développer des partenariats avec des ONG ou institutions externes")
        
        return recommandations

    # URL et représentation
    def get_absolute_url(self):
        """URL de détail du bureau/comité"""
        return reverse('bureau:detail', kwargs={'pk': self.pk})

    @property 
    def nom_avec_localisation(self):
        """Nom avec la zone d'intervention"""
        return f"{self.nom} ({self.get_zone_intervention_display()})"

    def __repr__(self):
        return f"<Bureau Kakony: {self.nom} - {self.get_type_bureau_display()}>"

"""

class BureauExecutif ( models.Model):

class BureauSuivi (models.Model):

class BureauLogistique (models.Model):

class BureauEducatif (models.Model):

class BureauSanté (models.Model):

class BureauEducatif (models.Model):

class BureauEnvoronement (models.Model):

class BureauCulture (models.Model):

class SalonPartenaire (models.Model):

class SalonReceiveur(models.Model):


"""


# ========== PUBLICATION =======
class Publication(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Publications", verbose_name="Auteur")
    titre = models.CharField(max_length=200, verbose_name="Titre ")
    contenu = models.TextField()
    image = models.ImageField(upload_to='publications/images/', blank=True, null=True, verbose_name="Image ")
    video = models.FileField(upload_to='publications/videos/', blank=True, null=True, verbose_name="Vidéo ")
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.titre

# ========== COMMENTAIRE ========
class Commentaire(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="Commentaires")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    texte = models.TextField()
    date_com = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire {self.auteur} sur {self.publication}"

# ========== A SUPPRIMER BIENTOTO
class like(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="likes")
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_like = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("publication", "utilisateur")
    def __str__(self):
        return f"{self.utilisateur} aime {self.publication}"



# ======== CONTACT =========
class Contact(models.Model):
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom ")
    prenom = models.CharField(max_length=200, blank=True, null=True, verbose_name="Prénom ")
    adresse = models.CharField(max_length=100, blank=True, null=True, verbose_name="Adresse ")
    image = models.ImageField(upload_to='static/image/ ')
    email = models.EmailField(verbose_name="Adresse .....@gmail.com ")
    contenu = models.TextField(blank=True)

    def __str__(self):
        return self.nom




from django.contrib.auth.models import User


class Payment(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('retard', 'En retard'),
    ]

    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cotisations")
    montant = models.DecimalField(max_digits=10, decimal_places=2, default='10000.00', verbose_name="Montant")
    date_create = models.DateTimeField(auto_now_add=True)
    mois = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_attente")

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ["-mois"]
        unique_together = ('utilisateur', 'mois')

    def __str__(self):
        return f"{self.utilisateur.username} - {self.mois.strftime('%B %Y')} - {self.get_status_display()}"

    def marquer_comme_paye(self, tresorier=None):
        """Marquer la cotisation comme payée par le trésorier"""
        self.status = 'paye'
        self.date_paiement = timezone.now()
        self.save()
        
        # Créer une entrée dans l'historique
        HistoriquePaiement.objects.create(
            cotisation=self,
            action="Paiement validé",
            montant=self.montant,
            utilisateur_admin=tresorier
        )

    @property
    def est_paye(self):
        return self.status == 'paye'




class Message(models.Model):
    """Messagerie de groupe - tous les utilisateurs dans une seule page"""
    envoyeur = models.ForeignKey(User, on_delete=models.CASCADE, 
        
    )
    contenu = models.TextField()
    fichier = models.FileField(upload_to='messages_fichiers/', null=True, blank=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_envoi']
    
    def __str__(self):
        return self.contenu