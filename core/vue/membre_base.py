from django.shortcuts import render 

def membre_base(request):
    return render(request, 'membre_base.html', {})