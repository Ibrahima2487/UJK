from django.urls import path
from . import views

urlpatterns = [
    # ======== DJANGO UTILS ======
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # ========= SURFACE WEB ===================
    path('', views.index, name='index'),
    path('about/', views.about, name="about"),
    path('base/', views.base, name="base"),
    path('connexion/', views.connexion, name="connexion"),
    path('actions/', views.actions, name='actions'),
    path('blog/', views.blog, name="blog"),
    path('gallery/', views.gallery, name="gallery"),

    # ============ MEMBRE WEB ==================
    path('membre_base/', views.membre_base, name='membre_base'),

    # ======= GALLERIEN ===============
    path('gallery_modifie/<int:pk>/', views.gallery_modifie, name='gallery_modifie'),
    path('gallery_status/', views.gallery_status, name='gallery_status'),
    path('gallery_supprime/<int:pk>/', views.gallery_supprime, name='gallery_supprime'),
    path('gallery_ajouter/', views.gallery_ajouter, name="gallery_ajouter"),


    # ======= TEMOIN ============
    path('temoin/', views.temoin, name='temoin'),
    path('temoin_create/', views.temoin_create, name="temoin_create"),
    path('temoin_details/<int:pk>/', views.temoin_details, name='temoin_details'),
    path('temoin_edit/<int:pk>/', views.temoin_edit, name='temoin_edit'),

    # =========== PROFILE ==============
    path('profile/', views.profile, name="profile"),
    path('profile_image/', views.profile_image, name="profile_image"),

    # =========== PRÉSIDENT PORTAILS ==============
    path('trone/', views.trone, name="trone"),

    # ============== COMPTE MEMBRE ===========
    path('membre_create/', views.membre_create, name="membre_create"),
    path('membre_status/', views.membre_status, name="membre_status"),
    path('membre_profile/<int:user_id>/', views.membre_profile, name="membre_profile"),

    # ================ ACTUALITÉ =============
    path('blog_status/', views.blog_status, name="blog_status"),
    path('blog_modifie/<int:pk>/', views.blog_modifie, name="blog_modifie"),
    path('blog_supprime/<int:pk>/', views.blog_supprime, name="blog_supprime"),
    path('blog_create/', views.blog_create, name="blog_create"),

    # ================ BUREAU =================
    path('bureau/', views.bureau, name="bureau"),
    path('bureau_details/<int:pk>/', views.bureau_details, name="bureau_details"),
    path('bureau_ajouter/', views.bureau_ajouter, name="bureau_ajouter"),
    path('bureau_modifie/<int:pk>/', views.bureau_modifie, name="bureau_modifie"),

    # ========= PUBLICATION ==============
    path('pub_create/', views.pub_create, name="pub_create"),
    path('pub_modifie/<int:pk>/', views.pub_modifie, name="pub_modifie"),

    
    path('pub_likes/<int:pk>/', views.pub_likes, name="pub_likes"),

    # ======= INFORMATION =================
    path('main_tails/<int:pk>/', views.main_details, name="main_details"),
    path('main/', views.main, name='main'),

    #========= COMMENTAIRE ===============
    path('commentaire_create/<int:pk>/', views.commentaire_create, name="commentaire_create"),
    path('comment_modifie/<int:pk>/', views.comment_modifie, name="comment_modifie"),
    path('comme_details/<int:pk>/', views.comme_details, name="comme_details"),

    # ======== COMPTABLE =================
    path('comptable/', views.comptable, name="comptable"),
    path('comptable_form/', views.comptable_form, name="comptable_form"),

    # ========= CONTACT =================
    path('contact/', views.contact, name="contact"),
    path('contact_status/', views.contact_status, name="contact_status"),

    # ========= INFORMATION DU PRROFILE EXTERNE ====
    path('profile_qr/<str:username>/', views.profile_qr, name='profile_qr'),

    # ========= CHAT =========================
    path('message/', views.message, name='message'),
    path('message_create/', views.message_create, name='message_create'),

]