from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.navigation import back_link

from .models import Folder, Project


def _visible_projects(request):
    """Kirgan foydalanuvchi qoralamalarni ham ko'radi."""
    qs = Project.objects.select_related("folder")
    if not request.user.is_authenticated:
        qs = qs.filter(is_published=True)
    return qs


def index(request):
    published = Q() if request.user.is_authenticated else Q(projects__is_published=True)
    folders = Folder.objects.annotate(
        project_count=Count("projects", filter=published, distinct=True)
    )
    loose = _visible_projects(request).filter(folder__isnull=True)
    return render(
        request,
        "portfolio/index.html",
        {
            "folders": folders,
            "loose_projects": loose,
            "total": _visible_projects(request).count(),
        },
    )


def folder_detail(request, slug):
    folder = get_object_or_404(Folder, slug=slug)
    projects = _visible_projects(request).filter(folder=folder)
    return render(
        request,
        "portfolio/folder.html",
        {
            "folder": folder,
            "projects": projects,
            "folders": Folder.objects.all(),
            "detail_page": True,
            "back_url": back_link(request, reverse("portfolio:index")),
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(_visible_projects(request), slug=slug)
    siblings = (
        _visible_projects(request)
        .filter(folder=project.folder)
        .exclude(pk=project.pk)[:3]
        if project.folder
        else _visible_projects(request).exclude(pk=project.pk)[:3]
    )
    parent = (
        project.folder.get_absolute_url() if project.folder else reverse("portfolio:index")
    )
    return render(
        request,
        "portfolio/project.html",
        {
            "project": project,
            "siblings": siblings,
            "images": project.images.all(),
            "detail_page": True,
            "back_url": back_link(request, parent),
        },
    )
