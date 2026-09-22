import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from blog.models import Article
from portfolio.models import Folder, Project

from .forms import MessageForm, StyledLoginForm
from .security import client_ip, record_attempt, reset_attempts, too_many
from .models import (
    Award, Education, Experience, LanguageSkill, SkillGroup, SlideItem,
)

logger = logging.getLogger("oldfox")


def home(request):
    context = {
        "slides": SlideItem.objects.filter(is_active=True),
        "articles": Article.objects.filter(is_published=True)[:3],
        "featured_projects": (
            Project.objects.filter(is_published=True, is_featured=True)
            .select_related("folder")[:3]
        ),
        "latest_projects": (
            Project.objects.filter(is_published=True)
            .select_related("folder")
            .order_by("-created_at")[:4]
        ),
        "experiences": Experience.objects.all()[:3],
        "skill_groups": SkillGroup.objects.prefetch_related("skills")[:3],
        "folders": Folder.objects.all()[:5],
        "project_count": Project.objects.filter(is_published=True).count(),
    }
    return render(request, "core/home.html", context)


def resume(request):
    context = {
        "experiences": Experience.objects.all(),
        "educations": Education.objects.all(),
        "skill_groups": SkillGroup.objects.prefetch_related("skills"),
        "awards": Award.objects.all(),
        "languages": LanguageSkill.objects.all(),
    }
    return render(request, "core/resume.html", context)


@require_http_methods(["GET", "POST"])
def contact(request):
    form = MessageForm()
    if request.method == "POST":
        ip = client_ip(request)
        if too_many("contact", ip, settings.CONTACT_RATE_LIMIT, 3600):
            messages.error(
                request, "Juda ko'p xabar yuborildi. Bir oz kutib, qayta urinib ko'ring."
            )
            return redirect("core:contact")

        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            record_attempt("contact", ip, 3600)
            messages.success(request, "Xabaringiz yuborildi. Tez orada javob beraman.")
            return redirect("core:contact")
        messages.error(request, "Shaklda xatolik bor, tekshirib qayta yuboring.")
    return render(request, "core/contact.html", {"form": form})


class ThrottledLoginView(auth_views.LoginView):
    """Kirish sahifasi — ketma-ket noto'g'ri urinishlar cheklanadi."""

    template_name = "registration/login.html"
    authentication_form = StyledLoginForm
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        ip = client_ip(request)
        if too_many("login", ip, settings.LOGIN_RATE_LIMIT, settings.LOGIN_RATE_WINDOW):
            logger.warning("Kirishga urinishlar chegarasi oshdi: %s", ip)
            form = self.get_form()
            form.add_error(
                None, "Juda ko'p urinish bo'ldi. 15 daqiqadan so'ng qayta urinib ko'ring."
            )
            return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        ip = client_ip(self.request)
        record_attempt("login", ip, settings.LOGIN_RATE_WINDOW)
        logger.warning("Muvaffaqiyatsiz kirish urinishi: %s", ip)
        return super().form_invalid(form)

    def form_valid(self, form):
        reset_attempts("login", client_ip(self.request))
        return super().form_valid(form)
