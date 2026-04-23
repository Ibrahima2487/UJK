from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from core.models import Utilisateur, User
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
from django.core.files import File
import time

@login_required
def profile(request, username=None):
    """
    UNE SEULE FONCTION QUI FAIT TOUT :
    - Affiche le profil
    - Génère le badge avec fond SVG/Image
    - Télécharge le badge
    - Aperçu du badge
    """
    # Récupérer l'utilisateur
    if username:
        user = get_object_or_404(User, username=username)
        try:
            utilisateur = Utilisateur.objects.get(user=user)
        except Utilisateur.DoesNotExist:
            utilisateur = Utilisateur.objects.create(user=user)
    else:
        try:
            utilisateur = Utilisateur.objects.get(user=request.user)
        except Utilisateur.DoesNotExist:
            utilisateur = Utilisateur.objects.create(user=request.user)
    
    peut_editer = (request.user == utilisateur.user or request.user.is_staff)
    action = request.GET.get('action')
    
    # ===== TÉLÉCHARGER BADGE =====
    if action == 'telecharger':
        if utilisateur.badge_png:
            response = HttpResponse(utilisateur.badge_png.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="badge_{utilisateur.user.username}.png"'
            return response
        else:
            messages.error(request, "Aucun badge disponible. Veuillez générer votre badge d'abord.")
            return redirect(request.path)
    
    # ===== APERÇU BADGE =====
    elif action == 'apercu':
        if utilisateur.badge_png:
            return HttpResponse(utilisateur.badge_png.read(), content_type='image/png')
        else:
            # Badge par défaut avec message
            badge = Image.new("RGB", (530, 650), "#f0f0f0")
            draw = ImageDraw.Draw(badge)
            try:
                font = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            draw.text((265, 325), "Badge non généré", fill="#666", font=font, anchor="mm")
            draw.text((265, 360), "Cliquez sur 'Générer Badge'", fill="#999", font=font, anchor="mm")
            response = HttpResponse(content_type='image/png')
            badge.save(response, 'PNG')
            return response
    
    # ===== GÉNÉRER BADGE (POST) =====
    if request.method == 'POST' and peut_editer:
        try:
            # === DIMENSIONS DU BADGE ===
            largeur, hauteur = 530, 650
            
           # === CRÉATION DU BADGE AVEC FOND BLANC ===
            badge = Image.new("RGB", (largeur, hauteur), "#FFF")
            draw = ImageDraw.Draw(badge)

            # Ajouter une bordure décorative
            draw.rectangle([(5, 5), (largeur-5, hauteur-5)], outline="#E0E0E0", width=2)
            draw.rectangle([(8, 8), (largeur-8, hauteur-8)], outline="#F5F5F5", width=1)


            
            draw = ImageDraw.Draw(badge)
            
            # Couleurs
            bleu_udjk = (9, 62, 100) 
            or_udjk = (266, 266, 100)
            
            
            draw.rectangle([(0, 0), (largeur, 80)], fill=bleu_udjk)
            draw.rectangle([(0, 70), (largeur, 80)], fill=or_udjk)
            
            # Polices
            try:
                font_titre = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 30)
                font_texte = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 20)
                font_petit = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 16)
            except:
                font_titre = ImageFont.load_default(25)
                font_texte = ImageFont.load_default(30)
                font_petit = ImageFont.load_default(20)
            
            # Texte en-tête
            draw.text((largeur//2, 25), "UNION DES JEUNES DE KAKONY", 
                      fill="white", font=font_texte, anchor="mm")
            draw.text((largeur//2, 50), "================UDJK=================", 
                      fill="white", font=font_petit, anchor="mm")
            
            # Photo profil
            centre_x = largeur // 2
            y_photo = 100
            taille_photo = 220
            
            # Logo UDJK
            try:
                logo_path = f"{settings.BASE_DIR}/media/profiles/logo.png"
                logo = Image.open(logo_path).convert("RGBA").resize((80, 80))
                badge.paste(logo, (10, 95), logo)
            except:
                pass

            # Gestion de la photo utilisateur
            if utilisateur.image:
                try:
                    user_image = Image.open(utilisateur.image.path).convert("RGB")
                    user_image = user_image.resize((taille_photo, taille_photo))
                    
                    # Masque circulaire
                    mask = Image.new('L', (taille_photo, taille_photo), 0)
                    draw_mask = ImageDraw.Draw(mask)
                    draw_mask.ellipse((0, 0, taille_photo, taille_photo), fill=255)
                    
                    badge.paste(user_image, (centre_x - taille_photo//2, y_photo), mask)
                except Exception as e:
                    # Si erreur avec l'image, utiliser le placeholder
                    draw.ellipse([(centre_x - taille_photo//2, y_photo), 
                                  (centre_x + taille_photo//2, y_photo + taille_photo)], 
                                 fill="#ddd", outline=bleu_udjk, width=4)
                    draw.text((centre_x, y_photo + taille_photo//2), 
                             utilisateur.user.username[0].upper(), 
                             fill=bleu_udjk, font=font_titre, anchor="mm")
            else:
                # Photo par défaut avec initiale
                draw.ellipse([(centre_x - taille_photo//2, y_photo), 
                              (centre_x + taille_photo//2, y_photo + taille_photo)], 
                             fill="#e8f4f8", outline=bleu_udjk, width=4)
                initiale = utilisateur.user.username[0].upper()
                try:
                    font_initiale = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 80)
                except:
                    font_initiale = font_titre
                draw.text((centre_x, y_photo + taille_photo//2), 
                         initiale, 
                         fill=bleu_udjk, font=font_initiale, anchor="mm")
            
            # Informations utilisateur
            y_info = y_photo + taille_photo + 30
            nom = utilisateur.user.get_full_name() or utilisateur.user.username
                
            draw.text((centre_x, y_info), nom.upper(), 
                      fill="#667eea", font=font_titre, anchor="mm")
            
            y_details = y_info + 40
            
            if utilisateur.adresse:
                draw.text((centre_x, y_details), f"Adresse: {utilisateur.adresse}", 
                          fill="#000", font=font_petit, anchor="mm")
                y_details += 25
            
            if utilisateur.numero:
                draw.text((centre_x, y_details), f"Tel: {utilisateur.numero}", 
                          fill="#000", font=font_petit, anchor="mm")
                y_details += 25
            
            date_joined = utilisateur.user.date_joined.strftime("%d/%m/%Y")
            draw.text((centre_x, y_details), f"Membre depuis: {date_joined}", 
                      fill="#000", font=font_petit, anchor="mm")
            
            # QR Code
            y_qr = y_details + 40
            try:
                qr_data = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/profile_qr/{utilisateur.user.username}/"
                qr_img = qrcode.make(qr_data, box_size=3)
                qr_img = qr_img.resize((120, 120))
                badge.paste(qr_img, (centre_x - 60, y_qr))
            except Exception as e:
                draw.rectangle([(centre_x - 60, y_qr), (centre_x + 60, y_qr + 120)], 
                               outline=bleu_udjk, width=2)
                draw.text((centre_x, y_qr + 60), "QR", fill="gray", font=font_texte, anchor="mm")
            
            # Pied de page
            draw.rectangle([(0, hauteur-60), (largeur, hauteur)], fill=bleu_udjk)
            draw.text((centre_x, hauteur-30), "ASSOCIATION OFFICIELLE UDJK", 
                      fill="#fff", font=font_petit, anchor="mm")
            
            # === SAUVEGARDER LE BADGE ===
            buffer = BytesIO()
            badge.save(buffer, format="PNG")
            buffer.seek(0)
            
            filename = f"badge_{utilisateur.user.username}_{int(time.time())}.png"
            
            # Supprimer l'ancien badge s'il existe
            if utilisateur.badge_png:
                utilisateur.badge_png.delete()
            
            utilisateur.badge_png.save(filename, File(buffer), save=True)
            messages.success(request, "✅ Badge généré avec succès !")
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la génération: {str(e)}")
        
        return redirect(request.path)
    
    # ===== AFFICHAGE DE LA PAGE =====
    context = {
        'utilisateur': utilisateur,
        'peut_editer': peut_editer,
        'has_badge': bool(utilisateur.badge_png),
        'timestamp': int(time.time()),
    }

    return render(request, 'profile.html', context)