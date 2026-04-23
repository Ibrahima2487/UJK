from django.shortcuts import render, redirect, get_object_or_404
from core.models import Commentaire
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def comment_delete(request, pk):
    comment = get_object_or_404(Commentaire, pk=pk)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Le commentaire a été supprimé avec succès.")
        return redirect("main")
    return render(request, 'comment_delete.html', {"comment": comment})