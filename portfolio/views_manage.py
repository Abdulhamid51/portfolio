from django.contrib import messages as flash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import FolderForm, ProjectForm, ProjectImageFormSet
from .models import Folder, Project


@login_required
def folder_form(request, pk=None):
    folder = get_object_or_404(Folder, pk=pk) if pk else None
    form = FolderForm(request.POST or None, request.FILES or None, instance=folder)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        flash.success(request, f"“{obj.name}” papkasi saqlandi.")
        return redirect(obj.get_absolute_url())
    return render(
        request,
        "manage/form.html",
        {
            "form": form,
            "page_title": "Papkani tahrirlash" if folder else "Yangi papka",
            "page_note": "Papka — portfolio sahifasidagi loyihalar to'plami.",
            "delete_url": reverse("manage:folder_delete", args=[folder.pk]) if folder else None,
            "cancel_url": reverse("portfolio:index"),
        },
    )


@login_required
def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == "POST":
        folder.delete()
        flash.success(request, "Papka o'chirildi. Ichidagi loyihalar papkasiz qoldi.")
        return redirect("portfolio:index")
    return render(
        request,
        "manage/confirm_delete.html",
        {
            "object": folder,
            "what": "Papka",
            "note": "Loyihalar o'chmaydi — ular “papkasiz” bo'limiga o'tadi.",
            "cancel_url": reverse("portfolio:index"),
        },
    )


@login_required
def project_form(request, pk=None):
    project = get_object_or_404(Project, pk=pk) if pk else None
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    formset = ProjectImageFormSet(
        request.POST or None, request.FILES or None, instance=project
    )
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        obj = form.save()
        formset.instance = obj
        formset.save()
        flash.success(request, f"“{obj.title}” saqlandi.")
        return redirect(obj.get_absolute_url())
    initial_folder = request.GET.get("papka")
    if project is None and initial_folder:
        form.fields["folder"].initial = Folder.objects.filter(slug=initial_folder).first()
    return render(
        request,
        "manage/project_form.html",
        {
            "form": form,
            "formset": formset,
            "project": project,
            "page_title": "Loyihani tahrirlash" if project else "Yangi loyiha",
            "delete_url": reverse("manage:project_delete", args=[project.pk]) if project else None,
            "cancel_url": project.get_absolute_url() if project else reverse("portfolio:index"),
        },
    )


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        folder = project.folder
        project.delete()
        flash.success(request, "Loyiha o'chirildi.")
        return redirect(folder.get_absolute_url() if folder else reverse("portfolio:index"))
    return render(
        request,
        "manage/confirm_delete.html",
        {
            "object": project,
            "what": "Loyiha",
            "cancel_url": project.get_absolute_url(),
        },
    )
