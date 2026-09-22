"""Kirgan foydalanuvchi uchun tahrirlash sahifalari."""
from django.urls import path

from blog import views_manage as blog_manage
from core import views_manage as core_manage
from portfolio import views_manage as portfolio_manage

app_name = "manage"

urlpatterns = [
    path("", core_manage.dashboard, name="dashboard"),
    path("profil/", core_manage.profile_edit, name="profile"),

    path("papka/yangi/", portfolio_manage.folder_form, name="folder_create"),
    path("papka/<int:pk>/tahrir/", portfolio_manage.folder_form, name="folder_update"),
    path("papka/<int:pk>/ochirish/", portfolio_manage.folder_delete, name="folder_delete"),

    path("loyiha/yangi/", portfolio_manage.project_form, name="project_create"),
    path("loyiha/<int:pk>/tahrir/", portfolio_manage.project_form, name="project_update"),
    path("loyiha/<int:pk>/ochirish/", portfolio_manage.project_delete, name="project_delete"),

    path("maqola/yangi/", blog_manage.article_form, name="article_create"),
    path("maqola/<int:pk>/tahrir/", blog_manage.article_form, name="article_update"),
    path("maqola/<int:pk>/ochirish/", blog_manage.article_delete, name="article_delete"),

    path("xabarlar/", core_manage.message_list, name="messages"),
    path("xabarlar/<int:pk>/belgilash/", core_manage.message_toggle, name="message_toggle"),
    path("xabarlar/<int:pk>/ochirish/", core_manage.message_delete, name="message_delete"),

    path("rasm-yuklash/", core_manage.editor_upload, name="editor_upload"),
    path("matnni-tozalash/", core_manage.assist_text, name="assist_text"),

    path("<slug:section>/yangi/", core_manage.section_create, name="section_create"),
    path("<slug:section>/<int:pk>/tahrir/", core_manage.section_update, name="section_update"),
    path("<slug:section>/<int:pk>/ochirish/", core_manage.section_delete, name="section_delete"),
]
