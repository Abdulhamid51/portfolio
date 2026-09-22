from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "rubric", "published_at", "is_published", "is_featured")
    list_filter = ("is_published", "is_featured", "rubric")
    search_fields = ("title", "lead", "body")
    prepopulated_fields = {"slug": ("title",)}
