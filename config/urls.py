from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from core.views import ThrottledLoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("kirish/", ThrottledLoginView.as_view(), name="login"),
    path("chiqish/", LogoutView.as_view(), name="logout"),
    path("manage/", include("config.manage_urls")),
    path("portfolio/", include("portfolio.urls")),
    path("maqolalar/", include("blog.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
