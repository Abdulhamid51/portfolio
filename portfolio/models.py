from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def unique_slug(instance, value, field_name="slug"):
    """Takrorlanmas slug hosil qiladi (kirill/lotin matnlar uchun ham)."""
    base = slugify(value, allow_unicode=False) or "yozuv"
    model = instance.__class__
    slug, counter = base, 2
    qs = model.objects.exclude(pk=instance.pk) if instance.pk else model.objects.all()
    while qs.filter(**{field_name: slug}).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


class Folder(models.Model):
    """Portfolio sahifasidagi “papka”. Loyihalar shu papkalar ichida turadi."""

    TONES = [
        ("manila", "Manila (odatiy)"),
        ("sand", "Qum"),
        ("sage", "Zaytun"),
        ("blush", "Pushti"),
        ("slate", "Ko'k-kulrang"),
    ]

    name = models.CharField("Papka nomi", max_length=100)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    description = models.CharField("Qisqa tavsif", max_length=240, blank=True)
    tone = models.CharField("Rang", max_length=20, choices=TONES, default="manila")
    cover = models.ImageField("Muqova rasm", upload_to="folders/", blank=True, null=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Papka"
        verbose_name_plural = "Papkalar"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:folder", args=[self.slug])


class Project(models.Model):
    STATUS = [
        ("done", "Yakunlangan"),
        ("ongoing", "Davom etmoqda"),
        ("concept", "Konsept"),
        ("archived", "Arxiv"),
    ]

    folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="projects", verbose_name="Papka",
    )
    title = models.CharField("Sarlavha", max_length=180)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    summary = models.CharField(
        "Qisqacha", max_length=300, blank=True,
        help_text="Ro'yxatlarda ko'rinadigan bir-ikki gap.",
    )
    body = models.TextField(
        "To'liq tavsif", blank=True,
        help_text="Boy matn muharriri: sarlavha, ro'yxat, rasm, kod, iqtibos.",
    )
    cover = models.ImageField("Muqova rasm", upload_to="projects/", blank=True, null=True)
    role = models.CharField("Mening rolim", max_length=140, blank=True)
    client = models.CharField("Buyurtmachi / jamoa", max_length=140, blank=True)
    tech = models.CharField(
        "Texnologiyalar", max_length=240, blank=True,
        help_text="Vergul bilan ajrating: Django, PostgreSQL, Figma",
    )
    year = models.PositiveIntegerField("Yil", blank=True, null=True)
    status = models.CharField("Holat", max_length=20, choices=STATUS, default="done")
    live_url = models.URLField("Jonli havola", blank=True)
    repo_url = models.URLField("Kod havolasi", blank=True)
    is_featured = models.BooleanField("Bosh sahifada", default=False)
    is_published = models.BooleanField("Saytda ko'rinsin", default=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "-year", "-created_at")
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:project", args=[self.slug])

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech.split(",") if t.strip()]


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images", verbose_name="Loyiha"
    )
    image = models.ImageField("Rasm", upload_to="projects/gallery/")
    caption = models.CharField("Izoh", max_length=200, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Loyiha rasmi"
        verbose_name_plural = "Loyiha rasmlari"

    def __str__(self):
        return self.caption or f"Rasm #{self.pk}"
