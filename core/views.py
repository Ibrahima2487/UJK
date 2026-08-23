from django.shortcuts import render

# ====== PARTIE SURFACE WEB =================
from .vue.index import index
from .vue.about import about
from .vue.base import base
from .vue.actions import actions
from .vue.blog import blog
from .vue.gallery import gallery
from .vue.profile import profile
from .vue.contact import contact
from .vue.equipe_list import equipe_list

# ====== PARTIE MEMBRE WEB ====================
from .vue.profile_image import profile_image
from .vue.trone import trone
from .vue.membre_base import membre_base

# ================ CRUD ======================
from .vue.membre_create import membre_create
from .vue.membre_status import membre_status
from .vue.membre_profile import membre_profile


# ======== TEMOIGNAGE ==========
from .vue.actions import temoin
from .vue.actions import temoin_create
from .vue.actions import temoin_details
from .vue.actions import temoin_edit

#====== PROJET ================
from .vue.projet import projet_list
from .vue.projet import projet_ajoute
from .vue.projet import projet_detail


from .vue.gallery import gallery_status
from .vue.gallery import gallery_modifie
from .vue.gallery import gallery_supprime
from .vue.gallery import gallery_ajouter

from .vue.blog import blog_status
from .vue.blog import blog_create
from .vue.blog import blog_modifie
from .vue.blog import blog_supprime

from .vue.bureau import bureau
from .vue.bureau import bureau_details
from .vue.bureau import bureau_ajouter
from .vue.bureau import bureau_modifie
from .vue.bureau import bureau_affecter

from .vue.pub_create import pub_create
from .vue.main import main
from .vue.main_details import main_details
from .vue.pub_modifie import pub_modifie


from .vue.commentaire_create import commentaire_create
from .vue.comme_details import comme_details
from .vue.comment_modifie import comment_modifie

#================================== DELETE
from .vue.pub_likes import pub_likes
#================================== 

# ================ COMPTABLITÉ ==========
from .vue.comptable import comptable
from .vue.comptable_form import comptable_form
from .vue.comptable import comptable_portail
from .vue.comptable import depense_liste
from .vue.comptable import depense_ajouter
from .vue.comptable import caisse_ajoute
from .vue.comptable import caisse_list
from .vue.comptable import caisse_modifie
from .vue.comptable import journal_liste
from .vue.comptable import journal_ajoute



from .vue.contact_status import contact_status

from .vue.profile_qr import profile_qr

from .vue.message import message
from .vue.message_create import message_create

#=============== UTILS ========================
from .vue.change_password import change_password
from .vue.deconnexion import deconnexion
from .vue.connexion import connexion



# ======= APPLICATION WEB HORS LIGNE
# views.py
def offline_view(request):
    return render(request, "offline.html")