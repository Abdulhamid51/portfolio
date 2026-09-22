from django.contrib import messages as flash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ArticleForm
from .models import Article


@login_required
def article_form(request, pk=None):
    article = get_object_or_404(Article, pk=pk) if pk else None
    form = ArticleForm(request.POST or None, request.FILES or None, instance=article)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        flash.success(request, f"“{obj.title}” saqlandi.")
        return redirect(obj.get_absolute_url())
    return render(
        request,
        "manage/article_form.html",
        {
            "form": form,
            "article": article,
            "page_title": "Maqolani tahrirlash" if article else "Yangi maqola",
            "delete_url": reverse("manage:article_delete", args=[article.pk]) if article else None,
            "cancel_url": article.get_absolute_url() if article else reverse("blog:index"),
        },
    )


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        flash.success(request, "Maqola o'chirildi.")
        return redirect("blog:index")
    return render(
        request,
        "manage/confirm_delete.html",
        {"object": article, "what": "Maqola", "cancel_url": article.get_absolute_url()},
    )
