from django.shortcuts import render, redirect
from core.forms import ContactForm
from core.models import Contact


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('contact')  
    else:
        form = ContactForm()
    return render(request, 'contact.html', {"form" : form})