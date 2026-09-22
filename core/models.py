import re

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

UZ_MONTHS = (
    "yan", "fev", "mar", "apr", "may", "iyn",
    "iyl", "avg", "sen", "okt", "noy", "dek",
)


def uz_month_year(value):
    """Sanani “mar 2024” ko'rinishida qaytaradi."""
    if not value:
        return ""
    return f"{UZ_MONTHS[value.month - 1]} {value.year}"


class SingletonModel(models.Model):
    """Faqat bitta yozuvga ega bo'ladigan model."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Profile(SingletonModel):
    full_name = models.CharField("To'liq ism", max_length=120, default="Ismingiz Familiyangiz")
    headline = models.CharField("Kasb / lavozim", max_length=160, blank=True)
    tagline = models.CharField(
        "Qisqa shior", max_length=240, blank=True,
        help_text="Bosh sahifadagi sarlavha ostida chiqadi.",
    )
    about = models.TextField(
        "Men haqimda", blank=True, help_text="Boy matn (rich text) qo'llab-quvvatlanadi.",
    )
    location = models.CharField("Manzil", max_length=120, blank=True)
    email = models.EmailField("E-pochta", blank=True)
    phone = models.CharField("Telefon", max_length=60, blank=True)
    website = models.URLField("Sayt", blank=True)
    photo = models.ImageField("Surat", upload_to="profile/", blank=True, null=True)
    resume_file = models.FileField("Rezyume fayli (PDF)", upload_to="resume/", blank=True, null=True)
    available_for_work = models.BooleanField("Ish takliflariga ochiqman", default=True)

    masthead = models.CharField(
        "Sayt nomi", max_length=80, blank=True,
        help_text="Sahifa tepasidagi katta sarlavha. Bo'sh bo'lsa ism ishlatiladi.",
    )
    edition_note = models.CharField(
        "Sarlavha yonidagi izoh", max_length=120, blank=True,
        help_text="Sahifa tepasida, sana yonida chiqadi. Masalan: “Toshkent”.",
    )
    footer_note = models.CharField("Pastki izoh", max_length=200, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profil"

    def __str__(self):
        return self.full_name

    @property
    def display_masthead(self):
        return self.masthead or self.full_name

    def get_absolute_url(self):
        return reverse("core:home")


class SocialLink(models.Model):
    label = models.CharField("Nomi", max_length=60)
    url = models.URLField("Havola")
    handle = models.CharField("Foydalanuvchi nomi", max_length=80, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Ijtimoiy havola"
        verbose_name_plural = "Ijtimoiy havolalar"

    def __str__(self):
        return self.label


class DatedEntry(models.Model):
    start_date = models.DateField("Boshlanish")
    end_date = models.DateField("Tugash", blank=True, null=True)
    is_current = models.BooleanField("Hozir davom etmoqda", default=False)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        abstract = True
        ordering = ("order", "-start_date")

    @property
    def period(self):
        start = uz_month_year(self.start_date)
        if self.is_current or not self.end_date:
            return f"{start} — hozir"
        return f"{start} — {uz_month_year(self.end_date)}"


class Experience(DatedEntry):
    role = models.CharField("Lavozim", max_length=140)
    company = models.CharField("Tashkilot", max_length=140)
    company_url = models.URLField("Tashkilot sayti", blank=True)
    location = models.CharField("Manzil", max_length=120, blank=True)
    description = models.TextField("Tavsif", blank=True, help_text="Boy matn.")

    class Meta(DatedEntry.Meta):
        verbose_name = "Tajriba"
        verbose_name_plural = "Ish tajribasi"

    def __str__(self):
        return f"{self.role} · {self.company}"


class Education(DatedEntry):
    degree = models.CharField("Yo'nalish / daraja", max_length=140)
    institution = models.CharField("O'quv muassasasi", max_length=140)
    location = models.CharField("Manzil", max_length=120, blank=True)
    description = models.TextField("Tavsif", blank=True, help_text="Boy matn.")

    class Meta(DatedEntry.Meta):
        verbose_name = "Ta'lim"
        verbose_name_plural = "Ta'lim"

    def __str__(self):
        return f"{self.degree} · {self.institution}"


class SkillGroup(models.Model):
    name = models.CharField("Guruh nomi", max_length=80)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Ko'nikma guruhi"
        verbose_name_plural = "Ko'nikma guruhlari"

    def __str__(self):
        return self.name


class Skill(models.Model):
    group = models.ForeignKey(
        SkillGroup, on_delete=models.CASCADE, related_name="skills", verbose_name="Guruh"
    )
    name = models.CharField("Ko'nikma", max_length=80)
    note = models.CharField("Izoh", max_length=80, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Ko'nikma"
        verbose_name_plural = "Ko'nikmalar"

    def __str__(self):
        return self.name


class Award(models.Model):
    title = models.CharField("Nomi", max_length=160)
    issuer = models.CharField("Beruvchi", max_length=140, blank=True)
    date = models.DateField("Sana", blank=True, null=True)
    url = models.URLField("Havola", blank=True)
    description = models.TextField("Tavsif", blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "-date")
        verbose_name = "Yutuq / sertifikat"
        verbose_name_plural = "Yutuqlar va sertifikatlar"

    def __str__(self):
        return self.title


class LanguageSkill(models.Model):
    name = models.CharField("Til", max_length=60)
    level = models.CharField("Daraja", max_length=60, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Til"
        verbose_name_plural = "Tillar"

    def __str__(self):
        return self.name


class SlideItem(models.Model):
    """Bosh sahifadagi slayder elementi: rasm, sarlavha va havola."""

    SIDES = [("left", "Chap tomon"), ("right", "O'ng tomon")]
    PANEL_STYLES = [
        ("glass", "Shaffof shisha — yorug'"),
        ("glass-dark", "Shaffof shisha — to'q"),
        ("paper", "Oddiy qog'oz (shaffofsiz)"),
    ]

    title = models.CharField("Sarlavha", max_length=140)
    subtitle = models.CharField("Qo'shimcha matn", max_length=220, blank=True)
    image = models.ImageField("Rasm", upload_to="slider/")
    url = models.CharField(
        "Havola", max_length=300, blank=True,
        help_text="To'liq manzil (https://…) yoki sayt ichidagi yo'l (/portfolio/).",
    )
    link_label = models.CharField(
        "Havola matni", max_length=60, blank=True,
        help_text="Bo'sh qoldirsangiz “Batafsil” yoziladi.",
    )
    side = models.CharField(
        "Karta tomoni", max_length=10, choices=SIDES, default="left",
        help_text="Sarlavha kartasi rasmning qaysi tomonida tursin.",
    )
    panel_style = models.CharField(
        "Karta uslubi", max_length=12, choices=PANEL_STYLES, default="glass",
    )
    panel_blur = models.PositiveSmallIntegerField(
        "Karta ortidagi xiralik", default=16,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="0 — shaffof shisha effekti o'chadi. Odatda 12–20 px yaxshi chiqadi.",
    )
    image_blur = models.PositiveSmallIntegerField(
        "Rasmning shu tomonidagi xiralik", default=12,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="0 — rasm xiralashtirilmaydi.",
    )
    blur_width = models.PositiveSmallIntegerField(
        "Xira maydon kengligi (%)", default=52,
        validators=[MinValueValidator(15), MaxValueValidator(100)],
        help_text="Rasmning necha foizi xiralashsin — qolgani ravshan qoladi.",
    )
    is_active = models.BooleanField("Ko'rsatilsin", default=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Slayder elementi"
        verbose_name_plural = "Slayder"

    def __str__(self):
        return self.title


class Message(models.Model):
    """Aloqa shakli orqali yuborilgan xabarlar."""

    name = models.CharField("Ism", max_length=120)
    contact = models.CharField(
        "Bog'lanish uchun", max_length=140,
        help_text="Telefon raqam, Telegram username yoki e-pochta — qaysi biri qulay bo'lsa.",
    )
    subject = models.CharField("Mavzu", max_length=160, blank=True)
    body = models.TextField("Xabar", max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField("O'qilgan", default=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"

    def __str__(self):
        return f"{self.name}: {self.subject or self.body[:40]}"

    @property
    def contact_href(self):
        """Yozilgan ma'lumotga qarab bosiladigan havola tayyorlaydi."""
        value = (self.contact or "").strip()
        if not value:
            return ""
        if "@" in value and " " not in value and not value.startswith("@"):
            return f"mailto:{value}"
        digits = re.sub(r"[^0-9+]", "", value)
        if len(digits) >= 7 and re.fullmatch(r"\+?[0-9]+", digits):
            return f"tel:{digits}"
        if value.startswith("@") and " " not in value:
            return f"https://t.me/{value[1:]}"
        return ""
