import json
import logging
import os
import uuid

from django.conf import settings
from django.contrib import messages as flash
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from portfolio.models import Folder, Project

from blog.models import Article

from . import ai
from .forms import (
    AwardForm, EducationForm, ExperienceForm, LanguageSkillForm, ProfileForm,
    SkillForm, SkillGroupForm, SlideItemForm, SocialLinkForm,
)
from .models import (
    Award, Education, Experience, LanguageSkill, Message, Profile, Skill,
    SkillGroup, SlideItem, SocialLink,
)
from .security import record_attempt, too_many

logger = logging.getLogger("oldfox")

# Bir xil CRUD oqimidan foydalanadigan bo'limlar
SECTIONS = {
    "tajriba": {
        "model": Experience, "form": ExperienceForm,
        "title": "Ish tajribasi", "one": "Tajriba", "anchor": "tajriba",
    },
    "talim": {
        "model": Education, "form": EducationForm,
        "title": "Ta'lim", "one": "Ta'lim yozuvi", "anchor": "talim",
    },
    "konikma-guruhi": {
        "model": SkillGroup, "form": SkillGroupForm,
        "title": "Ko'nikma guruhlari", "one": "Guruh", "anchor": "konikma",
    },
    "konikma": {
        "model": Skill, "form": SkillForm,
        "title": "Ko'nikmalar", "one": "Ko'nikma", "anchor": "konikma",
    },
    "yutuq": {
        "model": Award, "form": AwardForm,
        "title": "Yutuq va sertifikatlar", "one": "Yutuq", "anchor": "yutuq",
    },
    "til": {
        "model": LanguageSkill, "form": LanguageSkillForm,
        "title": "Tillar", "one": "Til", "anchor": "til",
    },
    "havola": {
        "model": SocialLink, "form": SocialLinkForm,
        "title": "Ijtimoiy havolalar", "one": "Havola", "anchor": "havola",
    },
    "slayd": {
        "model": SlideItem, "form": SlideItemForm,
        "title": "Slayder", "one": "Slayd", "anchor": "slayder",
        "template": "manage/slide_form.html",
    },
}


def _section(slug):
    if slug not in SECTIONS:
        from django.http import Http404

        raise Http404("Bunday bo'lim yo'q")
    return SECTIONS[slug]


@login_required
def dashboard(request):
    context = {
        "experiences": Experience.objects.all(),
        "educations": Education.objects.all(),
        "skill_groups": SkillGroup.objects.prefetch_related("skills"),
        "awards": Award.objects.all(),
        "languages": LanguageSkill.objects.all(),
        "social_links": SocialLink.objects.all(),
        "folders": Folder.objects.all(),
        "projects": Project.objects.select_related("folder"),
        "articles": Article.objects.all(),
        "slides": SlideItem.objects.all(),
        "unread": Message.objects.filter(is_read=False).count(),
        "messages_list": Message.objects.all()[:5],
    }
    return render(request, "manage/dashboard.html", context)


@login_required
def profile_edit(request):
    profile = Profile.load()
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        flash.success(request, "Profil yangilandi.")
        return redirect("manage:dashboard")
    return render(
        request,
        "manage/form.html",
        {
            "form": form,
            "page_title": "Profil va sarlavha",
            "page_note": "Sayt nomi, sarlavha va “Men haqimda” bo'limi.",
            "cancel_url": reverse("core:home"),
        },
    )


@login_required
def section_create(request, section):
    conf = _section(section)
    form = conf["form"](request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        flash.success(request, f"{conf['one']} qo'shildi.")
        return redirect(reverse("manage:dashboard") + f"#{conf['anchor']}")
    return render(
        request,
        conf.get("template", "manage/form.html"),
        {"form": form, "page_title": f"Yangi: {conf['one']}", "cancel_url": reverse("manage:dashboard")},
    )


@login_required
def section_update(request, section, pk):
    conf = _section(section)
    obj = get_object_or_404(conf["model"], pk=pk)
    form = conf["form"](request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        flash.success(request, f"{conf['one']} yangilandi.")
        return redirect(reverse("manage:dashboard") + f"#{conf['anchor']}")
    return render(
        request,
        conf.get("template", "manage/form.html"),
        {
            "form": form,
            "object": obj,
            "page_title": f"Tahrir: {conf['one']}",
            "page_note": str(obj),
            "delete_url": reverse("manage:section_delete", args=[section, pk]),
            "cancel_url": reverse("manage:dashboard"),
        },
    )


@login_required
def section_delete(request, section, pk):
    conf = _section(section)
    obj = get_object_or_404(conf["model"], pk=pk)
    if request.method == "POST":
        obj.delete()
        flash.success(request, f"{conf['one']} o'chirildi.")
        return redirect(reverse("manage:dashboard") + f"#{conf['anchor']}")
    return render(
        request,
        "manage/confirm_delete.html",
        {"object": obj, "what": conf["one"], "cancel_url": reverse("manage:dashboard")},
    )


@login_required
def message_list(request):
    qs = Message.objects.all()
    return render(request, "manage/messages.html", {"letters": qs})


@login_required
@require_POST
def message_toggle(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    return redirect("manage:messages")


@login_required
@require_POST
def message_delete(request, pk):
    get_object_or_404(Message, pk=pk).delete()
    flash.success(request, "Xabar o'chirildi.")
    return redirect("manage:messages")


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/avif"}


@login_required
@require_POST
def editor_upload(request):
    """Rich-text muharriridagi rasmni media papkaga yuklaydi."""
    file = request.FILES.get("image")
    if not file:
        return JsonResponse({"error": "Fayl topilmadi."}, status=400)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Faqat rasm fayllari qabul qilinadi."}, status=400)
    limit = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > limit:
        return JsonResponse(
            {"error": f"Rasm {settings.MAX_UPLOAD_SIZE_MB} MB dan katta bo'lmasin."},
            status=400,
        )
    ext = os.path.splitext(file.name)[1].lower() or ".jpg"
    today = timezone.localdate()
    name = f"editor/{today:%Y/%m}/{uuid.uuid4().hex}{ext}"
    saved = default_storage.save(name, file)
    return JsonResponse({"url": default_storage.url(saved)})


@login_required
@require_POST
def assist_text(request):
    """Muharrirdagi matnni Gemini orqali imlo va format jihatidan tozalaydi."""
    if not ai.is_enabled():
        return JsonResponse(
            {"error": "Gemini sozlanmagan. .env ga GEMINI_API_KEY qo'shing."}, status=503
        )

    who = f"user:{request.user.pk}"
    if too_many("assist", who, settings.ASSIST_RATE_LIMIT, 3600):
        return JsonResponse(
            {"error": "Soatlik chegara tugadi. Birozdan so'ng urinib ko'ring."}, status=429
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "So'rov noto'g'ri."}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "So'rov noto'g'ri."}, status=400)

    try:
        cleaned = ai.tidy_html(payload.get("html", ""))
    except ai.AssistError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception:  # kutilmagan xato — tafsilot foydalanuvchiga chiqmaydi
        logger.exception("Matnni tozalashda kutilmagan xato")
        return JsonResponse({"error": "Kutilmagan xato yuz berdi."}, status=500)

    record_attempt("assist", who, 3600)
    return JsonResponse({"html": cleaned, "model": settings.GEMINI_MODEL})
