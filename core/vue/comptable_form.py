from django.shortcuts import render, redirect
from core.forms import PaymentForm


def comptable_form(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('comptable')
    else:
        form = PaymentForm()
    return render(request, 'comptable_form.html', {"form" : form})