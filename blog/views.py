from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.navigation import back_link

from .models import Article


def _visible(request):
    qs = Article.objects.all()
    if not request.user.is_authenticated:
        qs = qs.filter(is_published=True)
    return qs


def index(request):
    articles = list(_visible(request))
    lead_article = articles[0] if articles else None
    return render(
        request,
        "blog/index.html",
        {"lead_article": lead_article, "articles": articles[1:], "total": len(articles)},
    )


def article_detail(request, slug):
    article = get_object_or_404(_visible(request), slug=slug)
    others = _visible(request).exclude(pk=article.pk)[:3]
    return render(
        request,
        "blog/article.html",
        {
            "article": article,
            "others": others,
            "detail_page": True,
            "back_url": back_link(request, reverse("blog:index")),
        },
    )
