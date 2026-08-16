from datetime import timedelta
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.models import Bureau, Caisse, Payment, Depense, JournalCaisse, FicheControle
from core.forms import PaymentForm, DepenseForm, FicheControleForm, CaisseForm, JournalCaisseForm


# ============================================================
#  Permission comptabilité
# ============================================================

def comptable_portail(request):
    return render(request, 'comptable_portail.html')


COULEURS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']


def _caisse_selectionnee(request):
    caisse_id = request.session.get('caisse_id')
    if caisse_id:
        try:
            return Caisse.objects.get(pk=caisse_id)
        except Caisse.DoesNotExist:
            pass
    return Caisse.get_ou_creer_principale()


def peut_gerer_comptabilite(user):
    return user.is_staff or user.is_superuser


def _fmt(n):
    """Formate un nombre avec POINT décimal pour SVG."""
    return "{:.2f}".format(float(n))


def _fmt0(n):
    """Formate sans décimale, avec point."""
    return "{:.0f}".format(float(n))


def _format_compact(val):
    n = float(val) if val else 0
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.0f}k"
    return f"{n:.0f}"


# ============================================================
# VUE PRINCIPALE
# ============================================================

@login_required
def comptable(request):
    # ── 1. Année ─────────────────────────────────────────────
    try:
        annee = int(request.GET.get('annee', timezone.now().year))
    except (ValueError, TypeError):
        annee = timezone.now().year

    # ── 2. Caisse ────────────────────────────────────────────
    caisse = _caisse_selectionnee(request)

    # ── 3. Stats ─────────────────────────────────────────────
    stats = Payment.statistiques_globales()

    # ── 4. Caisses enrichies ─────────────────────────────────
    solde_global = float(Caisse.solde_consolide())
    caisses_qs = Caisse.objects.all()
    caisses_principales_count = caisses_qs.filter(est_principale=True).count()

    for i, c in enumerate(caisses_qs):
        c.couleur = COULEURS[i % len(COULEURS)]
        c.pourcentage = (float(c.solde) / solde_global * 100) if solde_global > 0 else 0
        c.solde_compact = _format_compact(c.solde)

    # ── 5. KPI Entrées/Sorties du mois ───────────────────────
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mouvements_mois = caisse.journal.filter(date_operation__gte=debut_mois)
    total_entrees_mois = float(mouvements_mois.filter(type_operation='entree').aggregate(s=Sum('montant'))['s'] or 0)
    total_sorties_mois = float(mouvements_mois.filter(type_operation='sortie').aggregate(s=Sum('montant'))['s'] or 0)
    nombre_entrees = mouvements_mois.filter(type_operation='entree').count()
    nombre_sorties = mouvements_mois.filter(type_operation='sortie').count()
    total_mouvements_mois = total_entrees_mois + total_sorties_mois
    if total_mouvements_mois == 0:
        total_mouvements_mois = 1  # évite division par zéro

    # ── 6. Dépenses par catégorie ────────────────────────────
    depenses_categorie = (
        Depense.objects.filter(caisse=caisse).values('categorie')
        .annotate(total=Sum('montant')).order_by('-total')
    )
    labels_categories = dict(Depense.CATEGORIE_CHOICES)
    depenses_par_categorie = []
    total_depenses = 0
    for i, e in enumerate(depenses_categorie):
        total = float(e['total'] or 0)
        total_depenses += total
        depenses_par_categorie.append({
            'label': labels_categories.get(e['categorie'], e['categorie']),
            'total': total,
            'couleur': COULEURS[i % len(COULEURS)],
        })
    max_depense = max((d['total'] for d in depenses_par_categorie), default=1)
    for d in depenses_par_categorie:
        d['pct'] = (d['total'] / max_depense * 100) if max_depense > 0 else 0
        d['pct_total'] = (d['total'] / total_depenses * 100) if total_depenses > 0 else 0

    # ── 7. Taux paiement mensuel (histogramme SVG) ───────────
    mensuel = Payment.statistiques_mensuelles(annee)
    max_mensuel = max((float(m['total_attendu']) for m in mensuel), default=1)
    if max_mensuel == 0:
        max_mensuel = 1
    bar_width = 500 / 12
    mensuel_data = []
    taux_points = []
    for i, m in enumerate(mensuel):
        attendu = float(m['total_attendu'])
        paye = float(m['total_paye'])
        bar_h = (attendu / max_mensuel * 180) if max_mensuel else 0
        pay_h = (paye / max_mensuel * 180) if max_mensuel else 0
        mensuel_data.append({
            'label': m['label'],
            'bar_x': _fmt(i * bar_width + 4),
            'bar_y': _fmt(200 - bar_h),
            'bar_w': _fmt(bar_width - 8),
            'bar_h': _fmt(bar_h),
            'pay_x': _fmt(i * bar_width + 7),
            'pay_y': _fmt(200 - pay_h),
            'pay_w': _fmt(bar_width - 14),
            'pay_h': _fmt(pay_h),
        })
        taux_y = 200 - (m['taux_paiement'] / 100 * 180)
        taux_points.append({
            'x': _fmt(i * bar_width + bar_width / 2),
            'y': _fmt(taux_y),
        })
    taux_line_points = ' '.join(f"{p['x']},{p['y']}" for p in taux_points)

    # ── 8. Évolution solde (courbe SVG) ──────────────────────
    date_debut = timezone.now() - timedelta(days=60)
    mouvements_periode = list(caisse.journal.filter(date_operation__gte=date_debut).order_by('date_operation'))

    solde_initial = float(caisse.solde)
    for mvt in mouvements_periode:
        if mvt.type_operation == 'entree':
            solde_initial -= float(mvt.montant)
        else:
            solde_initial += float(mvt.montant)

    evolution_labels = []
    evolution_vals = []
    solde_courant = solde_initial
    for mvt in mouvements_periode:
        if mvt.type_operation == 'entree':
            solde_courant += float(mvt.montant)
        else:
            solde_courant -= float(mvt.montant)
        evolution_labels.append(mvt.date_operation.strftime('%d/%m'))
        evolution_vals.append(solde_courant)

    if not evolution_labels:
        evolution_labels = [timezone.now().strftime('%d/%m')]
        evolution_vals = [float(caisse.solde)]

    max_val = max(evolution_vals) if evolution_vals else 1
    min_val = min(evolution_vals) if evolution_vals else 0
    range_val = max_val - min_val or 1

    evolution_points = []
    for i, v in enumerate(evolution_vals):
        x = (i / (len(evolution_vals) - 1)) * 500 if len(evolution_vals) > 1 else 250
        y = 200 - ((v - min_val) / range_val * 170) - 15
        evolution_points.append({'x': _fmt(x), 'y': _fmt(y)})

    line_points = ' '.join(f"{p['x']},{p['y']}" for p in evolution_points)
    if evolution_points:
        area_points = f"{evolution_points[0]['x']},200 {line_points} {evolution_points[-1]['x']},200"
    else:
        area_points = ""

    # ── 9. Camembert SVG ─────────────────────────────────────
    pie_slices = []
    current_angle = -90
    for i, c in enumerate(caisses_qs):
        pct = (float(c.solde) / solde_global) if solde_global > 0 else 0
        arc = pct * 376.99
        pie_slices.append({
            'start_angle': _fmt(current_angle),
            'arc': _fmt(arc),
            'gap': _fmt(376.99 - arc),
            'color': c.couleur,
        })
        current_angle += pct * 360

    # ── 10. Derniers mouvements ──────────────────────────────
    derniers_mouvements = (
        caisse.journal
        .select_related('caisse', 'cotisation__utilisateur', 'depense')
        .order_by('-date_operation')[:10]
    )

    # ── 11. Contexte ─────────────────────────────────────────
    context = {
        'caisse': caisse,
        'caisses': caisses_qs,
        'caisses_principales_count': caisses_principales_count,
        'solde_consolide': solde_global,
        'solde_consolide_compact': _format_compact(solde_global),
        'stats': stats,
        'annee': annee,
        'annees_disponibles': [timezone.now().year, timezone.now().year - 1, timezone.now().year - 2],
        'date_du_jour': timezone.now().strftime('%A %d %B %Y').capitalize(),
        'total_entrees_mois': total_entrees_mois,
        'total_sorties_mois': total_sorties_mois,
        'total_mouvements_mois': total_mouvements_mois,
        'nombre_entrees': nombre_entrees,
        'nombre_sorties': nombre_sorties,
        'depenses_par_categorie': depenses_par_categorie,
        'mensuel_data': mensuel_data,
        'taux_points': taux_points,
        'taux_line_points': taux_line_points,
        'evolution_labels': evolution_labels,
        'evolution_points': evolution_points,
        'line_points': line_points,
        'area_points': area_points,
        'pie_slices': pie_slices,
        'derniers_mouvements': derniers_mouvements,
        'peut_gerer': peut_gerer_comptabilite(request.user),
    }

    # ── 12. JSON si AJAX ─────────────────────────────────────
    est_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if est_ajax or request.GET.get('format') == 'json':
        caisses_json = []
        for c in caisses_qs:
            caisses_json.append({
                'id': c.id, 'nom': c.nom, 'solde': str(c.solde),
                'est_principale': c.est_principale,
                'date_maj': c.date_maj.strftime('%d/%m/%Y %H:%M'),
            })
        return JsonResponse({
            'caisses': caisses_json,
            'stats': {k: str(v) if isinstance(v, Decimal) else v for k, v in stats.items()},
        })

    return render(request, 'comptable.html', context)

def caisse_list(request):
    caisses = Caisse.objects.all()
    context = {
        'caisses' : caisses
    }
    return render(request, 'caisse_list.html', context)

def caisse_ajoute(request):
    if request.method == "POST":
        form = CaisseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("caisse_list")
    else:
        form = CaisseForm()
        return render(request, 'caisse_ajoute.html', {"form" : form})


def caisse_modifie(request, pk):
    caisses = get_object_or_404(Caisse, pk=pk)
    if request.method == "POST":
        form = CaisseForm(request.POST, request.FILES, instance=caisses)
        if form.is_valid():
            form.save()
            return redirect("caisse_list")
    else:
        form = CaisseForm(instance=caisses)
    context = {
        'caisses' : caisses,
        'form' : form
    }
    return render(request, 'caisse_modifie.html', context)

@login_required
def cotisation_details(request, pk):
    cotisation = get_object_or_404(Payment.objects.select_related('utilisateur', 'caisse'), pk=pk)
    context = {
        'cotisation': cotisation,
        'historique': cotisation.historique.select_related('utilisateur_admin'),
        'peut_gerer': peut_gerer_comptabilite(request.user),
    }
    return render(request, 'cotisation_details.html', context)


@login_required
def cotisation_marquer_paye(request, pk):
    if not peut_gerer_comptabilite(request.user):
        return HttpResponseForbidden("Action réservée à la gestion de la comptabilité.")

    cotisation = get_object_or_404(Payment, pk=pk)

    if request.method != 'POST':
        return HttpResponseForbidden("Méthode non autorisée.")

    if cotisation.est_paye:
        messages.info(request, "Cette cotisation est déjà marquée payée.")
    else:
        # Le trésorier peut choisir la caisse de destination (multi-caisses) ;
        # sinon la caisse principale. Tout l'encaissement se joue dans Payment.save().
        cotisation.marquer_comme_paye(tresorier=request.user, caisse=_caisse_selectionnee(request))
        messages.success(request, f"Cotisation de {cotisation.utilisateur} marquée payée.")

    return redirect('cotisation_details', pk=cotisation.pk)


# ============================================================
#  DÉPENSES
# ============================================================
@login_required
def depense_liste(request):
    depenses = Depense.objects.select_related('caisse', 'projet', 'autorise_par').all()

    categorie = request.GET.get('categorie')
    if categorie:
        depenses = depenses.filter(categorie=categorie)

    caisse_id = request.GET.get('caisse')
    if caisse_id:
        depenses = depenses.filter(caisse_id=caisse_id)

    context = {
        'depenses': depenses,
        'peut_gerer': peut_gerer_comptabilite(request.user),
        'categorie_filtre': categorie or '',
        'caisses': Caisse.objects.all(),
    }
    return render(request, 'depense_liste.html', context)


@login_required
def depense_ajouter(request):
    if not peut_gerer_comptabilite(request.user):
        return HttpResponseForbidden("Action réservée à la gestion de la comptabilité.")

    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("depense_liste")
    else:
        form = DepenseForm()
        
    context = {'form': form}
    return render(request, 'depense_ajouter.html', context)


@login_required
def depense_details(request, pk):
    depense = get_object_or_404(Depense.objects.select_related('caisse', 'projet', 'autorise_par'), pk=pk)
    context = {'depense': depense}
    return render(request, 'depense_details.html', context)


# ============================================================
#  JOURNAL DE CAISSE
# ============================================================
@login_required
def journal_liste(request):
    caisse = _caisse_selectionnee(request)
    journal = JournalCaisse.objects.filter(caisse=caisse).select_related('cotisation__utilisateur', 'depense')

    type_operation = request.GET.get('type')
    if type_operation:
        journal = journal.filter(type_operation=type_operation)

    context = {
        'journal': journal,
        'caisse': caisse,
        'caisses': Caisse.objects.all(),
        'type_filtre': type_operation or '',
    }
    return render(request, 'journal_liste.html', context)

def journal_ajoute(request):
    if request.method == "POST":
        form = JournalCaisseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("journal_liste")
    else:
        form = JournalCaisseForm()
    return render(request, 'journal_ajoute.html', {"form" : form})


# ============================================================
#  FICHES DE CONTRÔLE
# ============================================================
@login_required
def fiche_controle_liste(request):
    fiches = FicheControle.objects.select_related('caisse', 'controleur').all()
    context = {
        'fiches': fiches,
        'peut_gerer': peut_gerer_comptabilite(request.user),
    }
    return render(request, 'fiche_controle_liste.html', context)


@login_required
def fiche_controle_ajouter(request):
    if not peut_gerer_comptabilite(request.user):
        return HttpResponseForbidden("Action réservée à la gestion de la comptabilité.")

    caisse = _caisse_selectionnee(request)

    if request.method == 'POST':
        form = FicheControleForm(request.POST)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.caisse = caisse
            fiche.controleur = request.user
            fiche.save()
            messages.success(request, f"Fiche de contrôle enregistrée — écart : {fiche.ecart}.")
            return redirect('fiche_controle_liste')
    else:
        form = FicheControleForm(initial={'solde_theorique': caisse.solde})

    context = {'form': form, 'caisses': Caisse.objects.all()}
    return render(request, 'fiche_controle_ajouter.html', context)


@login_required
def fiche_controle_details(request, pk):
    fiche = get_object_or_404(FicheControle.objects.select_related('caisse', 'controleur'), pk=pk)
    context = {'fiche': fiche}
    return render(request, 'fiche_controle_details.html', context)
