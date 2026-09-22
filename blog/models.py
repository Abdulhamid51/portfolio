import re

from django.db import models
from django.urls import reverse
from django.utils import timezone

from portfolio.models import unique_slug


class Article(models.Model):
    """Saytda chiqadigan maqola."""

    title = models.CharField("Sarlavha", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True, blank=True)
    rubric = models.CharField(
        "Rubrika", max_length=60, blank=True,
        help_text="Masalan: Texnologiya, Dizayn, Kundalik.",
    )
    lead = models.CharField(
        "Lid", max_length=300, blank=True,
        help_text="Sarlavha ostidagi bir-ikki gap; ro'yxatlarda ham ko'rinadi.",
    )
    body = models.TextField("Maqola matni", blank=True, help_text="Boy matn muharriri.")
    cover = models.ImageField("Muqova rasm", upload_to="articles/", blank=True, null=True)
    cover_caption = models.CharField("Rasm izohi", max_length=200, blank=True)
    published_at = models.DateField("Sana", default=timezone.localdate)
    is_published = models.BooleanField("Saytda ko'rinsin", default=True)
    is_featured = models.BooleanField("Bosh sahifada", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article", args=[self.slug])

    @property
    def word_count(self):
        text = re.sub(r"<[^>]+>", " ", self.body or "")
        return len([w for w in text.split() if w])

    @property
    def reading_minutes(self):
        """O'qish vaqti — daqiqada (minimum 1)."""
        return max(1, round(self.word_count / 180))
