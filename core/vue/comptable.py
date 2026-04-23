from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from core.models import Payment, User



@login_required
def comptable(request):
    """
    UNE SEULE FONCTION QUI FAIT TOUT :
    - Liste des paiements
    - Filtres par mois et année
    - Statistiques
    - Mes paiements (utilisateur connecté)
    - Marquer comme payé (staff uniquement)
    - Export PDF par mois
    """
    
    # ===== GESTION DE L'EXPORT PDF =====
    if request.GET.get('export_pdf') and request.user.is_staff:
        # Récupérer les paramètres de filtrage
        mois = request.GET.get('mois')
        annee = request.GET.get('annee')
        
        if not mois or not annee:
            messages.error(request, "❌ Veuillez sélectionner un mois et une année pour l'export PDF")
            return redirect('comptable')
        
        try:
            mois = int(mois)
            annee = int(annee)
        except (ValueError, TypeError):
            messages.error(request, "❌ Paramètres de mois/année invalides")
            return redirect('comptable')
        
        # Récupérer les paiements du mois
        paiements = Payment.objects.filter(
            mois__month=mois,
            mois__year=annee
        ).select_related('utilisateur').order_by('utilisateur__last_name')
        
        # Statistiques du mois
        stats = {
            'total': paiements.count(),
            'payes': paiements.filter(status='paye').count(),
            'en_attente': paiements.filter(status='en_attente').count(),
            'en_retard': paiements.filter(status='retard').count(),
            'montant_total': paiements.aggregate(Sum('montant'))['montant__sum'] or 0,
            'montant_paye': paiements.filter(status='paye').aggregate(Sum('montant'))['montant__sum'] or 0,
        }
        
        # Créer le buffer PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        style_heading = styles['Heading1']
        style_normal = styles['Normal']
        
        # Titre
        nom_mois = datetime(2000, mois, 1).strftime('%B')
        titre = f"Rapport des Cotisations - {nom_mois} {annee}"
        elements.append(Paragraph(titre, style_heading))
        elements.append(Spacer(1, 0.2*inch))
        
        # Statistiques
        stats_text = f"""
        <b>Statistiques du mois :</b><br/>
        Total cotisations: {stats['total']}<br/>
        Cotisations payées: {stats['payes']}<br/>
        En attente: {stats['en_attente']}<br/>
        En retard: {stats['en_retard']}<br/>
        Montant total: {stats['montant_total']} GNF<br/>
        Montant payé: {stats['montant_paye']} GNF
        """
        elements.append(Paragraph(stats_text, style_normal))
        elements.append(Spacer(1, 0.3*inch))
        
        # Tableau des paiements
        if paiements.exists():
            # En-têtes du tableau - SANS payment_method
            data = [['Utilisateur', 'Mois', 'Montant', 'Statut', 'Date création']]
            
            # Données
            for paiement in paiements:
                status_display = dict(Payment.STATUS_CHOICES).get(paiement.status, paiement.status)
                data.append([
                    f"{paiement.utilisateur.get_full_name() or paiement.utilisateur.username}",
                    paiement.mois.strftime('%m/%Y'),
                    f"{paiement.montant} GNF",
                    status_display,
                    paiement.date_create.strftime('%d/%m/%Y')
                ])
            
            # Créer le tableau avec 5 colonnes (sans méthode de paiement)
            table = Table(data, colWidths=[2.2*inch, 0.8*inch, 1*inch, 1.2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("Aucune cotisation pour ce mois.", style_normal))
        
        # Pied de page
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}", style_normal))
        elements.append(Paragraph(f"Par {request.user.get_full_name() or request.user.username}", style_normal))
        
        # Générer le PDF
        doc.build(elements)
        
        # Préparer la réponse
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cotisations_{nom_mois}_{annee}.pdf"'
        
        return response

    # ===== GESTION NORMALE DE LA PAGE COMPTABLE =====
    
    # Récupérer les paramètres
    mois_filtre = request.GET.get('mois', '')
    annee_filtre = request.GET.get('annee', '')
    status_filtre = request.GET.get('status', '')
    utilisateur_filtre = request.GET.get('utilisateur', '')
    action = request.GET.get('action', '')
    
    # ===== MARQUER COMME PAYÉ =====
    if action == 'payer' and request.user.is_staff:
        payment_id = request.GET.get('payment_id')
        if payment_id:
            paiement = get_object_or_404(Payment, id=payment_id)
            if paiement.status != 'paye':
                paiement.marquer_comme_paye(tresorier=request.user)
                messages.success(request, f"✅ Cotisation de {paiement.utilisateur.username} validée")
            else:
                messages.info(request, "ℹ️ Déjà payé")
            return redirect('comptable')
    
    # ===== REQUÊTE DE BASE =====
    # Si utilisateur normal : voir uniquement ses paiements
    # Si staff : voir tous les paiements
    if request.user.is_staff:
        paiements = Payment.objects.select_related('utilisateur').all()
    else:
        paiements = Payment.objects.filter(utilisateur=request.user)
    
    # ===== APPLIQUER LES FILTRES =====
    if mois_filtre:
        paiements = paiements.filter(mois__month=mois_filtre)
    
    if annee_filtre:
        paiements = paiements.filter(mois__year=annee_filtre)
    else:
        # Par défaut : année en cours
        annee_filtre = timezone.now().year
        paiements = paiements.filter(mois__year=annee_filtre)
    
    if status_filtre:
        paiements = paiements.filter(status=status_filtre)
    
    if utilisateur_filtre and request.user.is_staff:
        paiements = paiements.filter(
            Q(utilisateur__username__icontains=utilisateur_filtre) |
            Q(utilisateur__first_name__icontains=utilisateur_filtre) |
            Q(utilisateur__last_name__icontains=utilisateur_filtre)
        )
    
    # ===== STATISTIQUES GLOBALES =====
    stats = {
        'total_paiements': paiements.count(),
        'total_montant': paiements.aggregate(Sum('montant'))['montant__sum'] or 0,
        'payes': paiements.filter(status='paye').count(),
        'en_attente': paiements.filter(status='en_attente').count(),
        'en_retard': paiements.filter(status='retard').count(),
        'montant_paye': paiements.filter(status='paye').aggregate(Sum('montant'))['montant__sum'] or 0,
        'montant_attente': paiements.filter(status='en_attente').aggregate(Sum('montant'))['montant__sum'] or 0,
        'montant_retard': paiements.filter(status='retard').aggregate(Sum('montant'))['montant__sum'] or 0,
    }
    
    # ===== STATISTIQUES PAR MOIS =====
    stats_mensuelles = []
    for mois in range(1, 13):
        if request.user.is_staff:
            paiements_mois = Payment.objects.filter(
                mois__year=annee_filtre,
                mois__month=mois
            )
        else:
            paiements_mois = Payment.objects.filter(
                utilisateur=request.user,
                mois__year=annee_filtre,
                mois__month=mois
            )
        
        stats_mensuelles.append({
            'mois': mois,
            'nom_mois': datetime(2000, mois, 1).strftime('%B'),
            'total': paiements_mois.count(),
            'payes': paiements_mois.filter(status='paye').count(),
            'en_attente': paiements_mois.filter(status='en_attente').count(),
            'en_retard': paiements_mois.filter(status='retard').count(),
            'montant': paiements_mois.aggregate(Sum('montant'))['montant__sum'] or 0,
        })
    
    # ===== ANNÉES DISPONIBLES =====
    if request.user.is_staff:
        annees_disponibles = Payment.objects.dates('mois', 'year', order='DESC')
    else:
        annees_disponibles = Payment.objects.filter(
            utilisateur=request.user
        ).dates('mois', 'year', order='DESC')
    
    # ===== MOIS DISPONIBLES =====
    mois_disponibles = [
        {'num': 1, 'nom': 'Janvier'},
        {'num': 2, 'nom': 'Février'},
        {'num': 3, 'nom': 'Mars'},
        {'num': 4, 'nom': 'Avril'},
        {'num': 5, 'nom': 'Mai'},
        {'num': 6, 'nom': 'Juin'},
        {'num': 7, 'nom': 'Juillet'},
        {'num': 8, 'nom': 'Août'},
        {'num': 9, 'nom': 'Septembre'},
        {'num': 10, 'nom': 'Octobre'},
        {'num': 11, 'nom': 'Novembre'},
        {'num': 12, 'nom': 'Décembre'},
    ]
    
    # ===== VÉRIFIER SI ON PEUT EXPORTER =====
    peut_exporter = bool(mois_filtre and annee_filtre and request.user.is_staff)
    
    context = {
        'paiements': paiements,
        'stats': stats,
        'stats_mensuelles': stats_mensuelles,
        'annees_disponibles': annees_disponibles,
        'mois_disponibles': mois_disponibles,
        'mois_filtre': mois_filtre,
        'annee_filtre': annee_filtre,
        'status_filtre': status_filtre,
        'utilisateur_filtre': utilisateur_filtre,
        'status_choices': Payment.STATUS_CHOICES,
        'is_staff': request.user.is_staff,
        'peut_exporter': peut_exporter,
    }
    
    return render(request, 'comptable.html', context)