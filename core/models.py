from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator #valideurs pour les champs
from django.utils.text import slugify 
from django.utils import timezone
import os
from datetime import date, datetime, timedelta
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
from django.db import models, transaction
import uuid
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files import File
from django.conf import settings
import qrcode
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


# ========= UTILISATEUR ======== 


# ========= UTILISATEUR (version allégée) ========
class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numero = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='profiles/')
    adresse = models.CharField(max_length=100, default="Kakony")

    # Identifiant public non-devinable pour l'URL de profil (remplace le pk)
    profil_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Statut en ligne — mis à jour par les signaux login/logout ci-dessous
    en_ligne = models.BooleanField(default=False)
    derniere_activite = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    

    

    def bureaux_affectes(self):
        """Tous les Bureaux où ce membre a un poste formel actif (accès complet)."""
        return Bureau.objects.filter(
            affectations__membre=self, affectations__actif=True
        ).distinct()

    def bureau_redirection(self):
        """
        Pour la vue qui gère le clic sur la page BUREAU :
        - un seul Bureau affecté -> retourne ce Bureau (redirection directe)
        - plusieurs -> retourne None (la vue affiche la liste de choix)
        """
        bureaux = list(self.bureaux_affectes())
        return bureaux[0] if len(bureaux) == 1 else None

  


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






# --- Signaux : en_ligne = True dès la connexion, False à la déconnexion ---
# NB : ceci ne couvre pas la fermeture d'onglet sans déconnexion explicite.
# Si tu veux couvrir ce cas plus tard, on pourra ajouter un middleware qui
# repasse en_ligne à False après N minutes d'inactivité (session expirée).

@receiver(user_logged_in)
def _marquer_en_ligne(sender, user, request, **kwargs):
    Utilisateur.objects.filter(user=user).update(
        en_ligne=True, derniere_activite=timezone.now()
    )


@receiver(user_logged_out)
def _marquer_hors_ligne(sender, user, request, **kwargs):
    if user is not None:
        Utilisateur.objects.filter(user=user).update(en_ligne=False)


# ========= RÉUNION (globale, toute l'association) ========
class Reunion(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('tenue', 'Tenue'),
        ('annulee', 'Annulée'),
        ('reportee', 'Reportée'),
    ]

    date_reunion = models.DateField(verbose_name="Date")
    lieu = models.CharField(max_length=200, verbose_name="Lieu")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    ordre_du_jour = models.TextField(verbose_name="Ordre du jour")
    decisions_prises = models.TextField(blank=True, verbose_name="Décisions prises")
    responsable_cr = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reunions_compte_rendu', verbose_name="Responsable du CR"
    )
    # Assomption : liste des présents utile pour le suivi — dis-moi si tu ne le veux pas.
    participants = models.ManyToManyField(User, blank=True, related_name='reunions')
    observations = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_reunion']

    def __str__(self):
        return f"Réunion du {self.date_reunion} ({self.get_statut_display()})"


# ========= PROJET ========
# Assomption sur les champs (le point 5 était juste "PROJET ..") — à ajuster.
class Projet(models.Model):
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('suspendu', 'Suspendu'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='projets_responsable'
    )
    date_debut = models.DateField()
    date_fin_prevue = models.DateField(null=True, blank=True)
    date_fin_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    budget_prevu = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    beneficiaires_directs = models.PositiveIntegerField(default=0)
    beneficiaires_indirects = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom

    @property
    def depense_totale(self):
        return self.depenses.aggregate(total=models.Sum('montant'))['total'] or Decimal('0')

    @property
    def solde_restant(self):
        return self.budget_prevu - self.depense_totale


# ========= COMPTABILITÉ ========
# Choix retenu en l'absence de préférence : une Caisse globale pour l'UJK,
# facile à faire évoluer en "une Caisse par Bureau" plus tard si besoin.
class Caisse(models.Model):
    nom = models.CharField(max_length=100, default="Caisse UJK")
    solde = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    est_principale = models.BooleanField(
        default=False,
        help_text="Caisse utilisée par défaut quand aucune n'est précisée (une seule à la fois)"
    )
    date_maj = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} — Solde : {self.solde}"

    def save(self, *args, **kwargs):
        # Une seule caisse principale à la fois
        if self.est_principale:
            Caisse.objects.exclude(pk=self.pk).update(est_principale=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_ou_creer_principale(cls):
        """Renvoie toujours une caisse utilisable — jamais None."""
        caisse = cls.objects.filter(est_principale=True).first()
        if caisse:
            return caisse
        caisse = cls.objects.first()
        if caisse:
            caisse.est_principale = True
            caisse.save(update_fields=['est_principale'])
            return caisse
        return cls.objects.create(nom="Caisse UJK", est_principale=True)

    def deposer(self, montant):
        with transaction.atomic():
            c = Caisse.objects.select_for_update().get(pk=self.pk)
            c.solde += montant
            c.save(update_fields=['solde', 'date_maj'])
            self.solde = c.solde

    def retirer(self, montant):
        with transaction.atomic():
            c = Caisse.objects.select_for_update().get(pk=self.pk)
            if montant > c.solde:
                raise ValidationError(
                    f"Fonds insuffisants dans « {c.nom} » (solde : {c.solde}, demandé : {montant})"
                )
            c.solde -= montant
            c.save(update_fields=['solde', 'date_maj'])
            self.solde = c.solde

    def recalculer_solde(self):
        """Reconstitue le solde à partir du journal — source de vérité comptable.
        À utiliser pour les Fiches de contrôle / audit."""
        agg = self.journal.aggregate(
            entrees=models.Sum('montant', filter=models.Q(type_operation='entree')),
            sorties=models.Sum('montant', filter=models.Q(type_operation='sortie')),
        )
        solde_reel = (agg['entrees'] or Decimal('0')) - (agg['sorties'] or Decimal('0'))
        self.solde = solde_reel
        self.save(update_fields=['solde', 'date_maj'])
        return solde_reel

    @classmethod
    def solde_consolide(cls):
        """Somme de toutes les caisses — vue globale multi-caisses."""
        return cls.objects.aggregate(total=models.Sum('solde'))['total'] or Decimal('0')

    @classmethod
    def repartition(cls):
        """Pour un graphe en camembert : solde par caisse."""
        return list(cls.objects.values('nom', 'solde').order_by('-solde'))


class JournalCaisse(models.Model):
    TYPE_CHOICES = [('entree', 'Entrée'), ('sortie', 'Sortie')]

    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE, related_name='journal')
    type_operation = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    libelle = models.CharField(max_length=200)
    cotisation = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries'
    )
    depense = models.ForeignKey(
        'Depense', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries'
    )
    date_operation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_operation']

    def __str__(self):
        return f"{self.get_type_operation_display()} — {self.montant} ({self.date_operation:%d/%m/%Y})"


class Depense(models.Model):
    CATEGORIE_CHOICES = [
        ('fonctionnement', 'Fonctionnement'),
        ('projet', 'Projet'),
        ('evenement', 'Événement'),
        ('materiel', 'Matériel'),
        ('autre', 'Autre'),
    ]

    caisse = models.ForeignKey(Caisse, on_delete=models.PROTECT, related_name='depenses')
    projet = models.ForeignKey('Projet', on_delete=models.SET_NULL, null=True, blank=True, related_name='depenses')
    libelle = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='fonctionnement')
    justificatif = models.FileField(upload_to='comptabilite/justificatifs/', blank=True, null=True)
    autorise_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='depenses_autorisees')
    date_depense = models.DateField(default=timezone.now)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_depense']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                super().save(*args, **kwargs)
                self.caisse.retirer(self.montant)
                JournalCaisse.objects.create(
                    caisse=self.caisse, type_operation='sortie',
                    montant=self.montant, libelle=self.libelle, depense=self,
                )
            else:
                ancien = Depense.objects.get(pk=self.pk)
                super().save(*args, **kwargs)
                diff = self.montant - ancien.montant
                if diff != 0:
                    if diff > 0:
                        self.caisse.retirer(diff)
                    else:
                        self.caisse.deposer(-diff)
                    JournalCaisse.objects.create(
                        caisse=self.caisse,
                        type_operation='sortie' if diff > 0 else 'entree',
                        montant=abs(diff),
                        libelle=f"Ajustement — {self.libelle}",
                        depense=self,
                    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.caisse.deposer(self.montant)
            JournalCaisse.objects.create(
                caisse=self.caisse, type_operation='entree',
                montant=self.montant, libelle=f"Annulation dépense — {self.libelle}",
            )
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.libelle} — {self.montant}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('retard', 'En retard'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cotisations")
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10000.00'))
    date_create = models.DateTimeField(auto_now_add=True)
    mois = models.DateField(default=timezone.now, verbose_name="Mois concerné")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_attente")
    date_paiement = models.DateTimeField(null=True, blank=True)
    caisse = models.ForeignKey(Caisse, on_delete=models.SET_NULL, null=True, blank=True, related_name='cotisations')

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ["-mois"]
        unique_together = ('utilisateur', 'mois')

    def __str__(self):
        return f"{self.utilisateur.username} - {self.mois.strftime('%B %Y')} - {self.get_status_display()}"

    @property
    def est_paye(self):
        return self.status == 'paye'

    @property
    def est_en_retard(self):
        return self.status != 'paye' and self.mois.replace(day=28) < timezone.now().date()

    def verifier_retard(self):
        if self.est_en_retard and self.status != 'retard':
            self.status = 'retard'
            self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        """LE cœur de la comptabilité : quel que soit le chemin utilisé pour passer
        un paiement à 'paye' (admin, vue, shell...), l'argent arrive en caisse ici,
        une seule fois. Aucune autre méthode n'a le droit de bouger la caisse."""
        ancien_statut = None
        if self.pk:
            ancien_statut = Payment.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        if self.status == 'paye' and self.caisse_id is None:
            self.caisse = Caisse.get_ou_creer_principale()

        with transaction.atomic():
            devient_paye = self.status == 'paye' and ancien_statut != 'paye'
            if devient_paye and self.date_paiement is None:
                self.date_paiement = timezone.now()

            super().save(*args, **kwargs)

            if devient_paye and self.caisse:
                self.caisse.deposer(self.montant)
                JournalCaisse.objects.create(
                    caisse=self.caisse, type_operation='entree',
                    montant=self.montant,
                    libelle=f"Cotisation {self.utilisateur.username} — {self.mois:%B %Y}",
                    cotisation=self,
                )
            elif ancien_statut == 'paye' and self.status != 'paye' and self.caisse:
                # Annulation d'un paiement déjà encaissé : on sort l'argent
                self.caisse.retirer(self.montant)
                JournalCaisse.objects.create(
                    caisse=self.caisse, type_operation='sortie',
                    montant=self.montant,
                    libelle=f"Annulation cotisation {self.utilisateur.username} — {self.mois:%B %Y}",
                    cotisation=self,
                )

    def marquer_comme_paye(self, tresorier=None, caisse=None):
        """Simple raccourci — toute la vraie logique est dans save()."""
        if caisse is not None:
            self.caisse = caisse
        self.status = 'paye'
        self.save()
        HistoriquePaiement.objects.create(
            cotisation=self, action="Paiement validé",
            montant=self.montant, utilisateur_admin=tresorier,
        )

    @classmethod
    def statistiques_globales(cls):
        agg = cls.objects.aggregate(
            total_attendu=models.Sum('montant'),
            total_paye=models.Sum('montant', filter=models.Q(status='paye')),
        )
        return {
            'total_attendu': agg['total_attendu'] or Decimal('0'),
            'total_paye': agg['total_paye'] or Decimal('0'),
            'nombre_en_retard': cls.objects.filter(status='retard').count(),
            'nombre_en_attente': cls.objects.filter(status='en_attente').count(),
        }

    @classmethod
    def statistiques_mensuelles(cls, annee=None):
        """Taux de paiement (%) par mois — prêt pour un graphe (labels + data)."""
        annee = annee or timezone.now().year
        resultats = []
        for m in range(1, 13):
            qs = cls.objects.filter(mois__year=annee, mois__month=m)
            agg = qs.aggregate(
                total_attendu=models.Sum('montant'),
                total_paye=models.Sum('montant', filter=models.Q(status='paye')),
            )
            attendu = agg['total_attendu'] or Decimal('0')
            paye = agg['total_paye'] or Decimal('0')
            taux = float(paye / attendu * 100) if attendu > 0 else 0.0
            resultats.append({
                'mois': m,
                'label': date(annee, m, 1).strftime('%B'),
                'total_attendu': attendu,
                'total_paye': paye,
                'taux_paiement': round(taux, 1),
                'nombre_en_retard': qs.filter(status='retard').count(),
            })
        return resultats


class HistoriquePaiement(models.Model):
    cotisation = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    utilisateur_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations_paiement')
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.action} — {self.cotisation} — {self.date_action:%d/%m/%Y}"


class FicheControle(models.Model):
    STATUT_CHOICES = [
        ('conforme', 'Conforme'),
        ('ecart', 'Écart constaté'),
        ('en_cours', 'En cours de vérification'),
    ]

    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE, related_name='fiches_controle')
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    solde_theorique = models.DecimalField(max_digits=14, decimal_places=2)
    solde_reel_constate = models.DecimalField(max_digits=14, decimal_places=2)
    ecart = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'), editable=False)
    controleur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fiches_controle')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    observations = models.TextField(blank=True)
    date_controle = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.ecart = self.solde_reel_constate - self.solde_theorique
        self.statut = 'conforme' if self.ecart == 0 else 'ecart'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contrôle {self.periode_debut:%m/%Y} — {self.get_statut_display()}"

# ============================================================
#  BUREAUX — affectation des membres, règles d'accès, chat interne
#  Règle d'accès retenue (confirmée en discussion) :
#   - "central" = Exécutif, Logistique, Suivi-évaluation : accès de VISITE
#     mutuel entre eux, + accès de VISITE (lecture seule) vers les 4 bureaux
#     opérationnels.
#   - accès COMPLET (écrire dans le chat, agir comme membre) uniquement
#     là où le membre a une Affectation active.
#   - un membre peut avoir une Affectation active dans plusieurs Bureaux.
#   - seuls les responsables de Logistique et Exécutif peuvent créer une
#     Affectation (formulaire réservé — vérifié via Bureau.peut_affecter_membres).
# ============================================================

class Bureau(models.Model):
    TYPE_CHOICES = [
        ('EXECUTIF', 'Bureau Exécutif'),
        ('LOGISTIQUE', 'Bureau Logistique'),
        ('SUIVI_EVALUATION', 'Bureau Suivi-évaluation'),
        ('EDUCATIF', 'Bureau Educatif'),
        ('SANTE', 'Bureau Santé'),
        ('CULTUREL', 'Bureau Culturel'),
        ('ENVIRONNEMENT', 'Bureau Environnement'),
    ]
    # Trio central : accès mutuel entre eux + visite (lecture seule) des bureaux opérationnels
    TYPES_CENTRAUX = {'EXECUTIF', 'LOGISTIQUE', 'SUIVI_EVALUATION'}
    # Seuls ces deux bureaux peuvent affecter des membres
    TYPES_HABILITES_AFFECTATION = {'LOGISTIQUE', 'EXECUTIF'}

    nom = models.CharField(max_length=200)
    type_bureau = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    date_creation = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Bureau"
        verbose_name_plural = "Bureaux"
        ordering = ['type_bureau']

    def __str__(self):
        return self.nom

    @property
    def est_central(self):
        return self.type_bureau in self.TYPES_CENTRAUX

    def utilisateur_a_acces(self, user):
        """Accès en consultation (membre direct, ou visiteur via un bureau central)."""
        if not user or not user.is_authenticated:
            return False
        if Affectation.objects.filter(bureau=self, membre__user=user, actif=True).exists():
            return True
        return Affectation.objects.filter(
            bureau__type_bureau__in=self.TYPES_CENTRAUX,
            membre__user=user, actif=True,
        ).exists()

    def utilisateur_peut_publier(self, user):
        """Accès complet : uniquement en cas d'affectation directe et active."""
        if not user or not user.is_authenticated:
            return False
        return Affectation.objects.filter(bureau=self, membre__user=user, actif=True).exists()

    @classmethod
    def peut_affecter_membres(cls, user):
        """Seuls les responsables actifs de Logistique ou Exécutif peuvent affecter des membres."""
        if not user or not user.is_authenticated:
            return False
        return Affectation.objects.filter(
            bureau__type_bureau__in=cls.TYPES_HABILITES_AFFECTATION,
            membre__user=user, actif=True,
        ).exists()


class Affectation(models.Model):
    """Table de liaison Membre <-> Bureau avec poste. Un membre peut en avoir plusieurs."""

    membre = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='affectations'
    )
    bureau = models.ForeignKey(
        Bureau, on_delete=models.CASCADE, related_name='affectations'
    )
    poste = models.CharField(
        max_length=100,
        help_text="Ex: Président, Vice-Président, Secrétaire Général, Conseiller, "
                   "Directeur, Membre..."
    )
    est_responsable = models.BooleanField(
        default=False,
        help_text="Poste de responsable du bureau (donne le droit d'affecter des "
                   "membres si le bureau est Logistique ou Exécutif)"
    )
    actif = models.BooleanField(default=True)
    affecte_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='affectations_realisees'
    )
    date_affectation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Affectation"
        verbose_name_plural = "Affectations"
        unique_together = ('membre', 'bureau', 'poste')
        ordering = ['-date_affectation']

    

    def __str__(self):
        return f"{self.membre} → {self.bureau} ({self.poste})"


class MessageBureau(models.Model):
    """Chat interne à un Bureau — réservé aux membres ayant une Affectation active."""

    bureau = models.ForeignKey(Bureau, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_bureau')
    contenu = models.TextField()
    fichier = models.FileField(upload_to='bureaux/messages/', null=True, blank=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message de Bureau"
        verbose_name_plural = "Messages de Bureau"
        ordering = ['date_envoi']

    def clean(self):
        if not self.bureau.utilisateur_peut_publier(self.auteur):
            raise ValidationError(
                "Cet utilisateur n'a pas de poste actif dans ce Bureau : accès lecture "
                "seule ou aucun accès, impossible d'écrire dans ce chat."
            )

    def __str__(self):
        return f"{self.auteur} dans {self.bureau} — {self.date_envoi:%d/%m/%Y %H:%M}"