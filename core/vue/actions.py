from django.shortcuts import render, redirect, get_object_or_404
from core.forms import TemoinForm
from core.models import Temoin

def actions(request):
    return render(request, 'actions.html')


def temoin (request):
    temoins = Temoin.objects.all()

    return render(request, 'temoin.html', {"temoins" : temoins})


def temoin_create(request):
    if request.method == "POST":
        form = TemoinForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect ('trone')
    else:
        form = TemoinForm()
    return render(request, 'temoin_create.html', {"form" : form})


# ===== DETAILS ===
def temoin_details (request, pk):
    temoins = get_object_or_404(Temoin, pk=pk)

    context = {
        'temoins', temoins
    }

    return render(request, 'temoin_details.html', context)


# ========= MODIFIE ======

def temoin_edit (request, pk):
    temoins = get_object_or_404(Temoin, pk=pk)
    if request.method == "POST":
        form = TemoinForm(request.POST, request.FILES, instance=temoins)
        if form.is_valid():
            form.save()
            return redirect('trone')
    else:
        form = TemoinForm(instance=temoins)

    context = {
        'temoins', temoins,
        'form', form
    }
    return render(request, 'temoin_edit.html', context)