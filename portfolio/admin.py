from django.contrib import admin

from .models import Folder, Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "tone", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "folder", "year", "status", "is_featured", "is_published")
    list_filter = ("folder", "status", "is_featured", "is_published")
    search_fields = ("title", "summary", "tech")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]
