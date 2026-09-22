from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.index, name="index"),
    path("loyiha/<slug:slug>/", views.project_detail, name="project"),
    path("<slug:slug>/", views.folder_detail, name="folder"),
]
