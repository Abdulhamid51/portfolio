"""Rasm maydonlari uchun kesish (crop) oynasi bilan ishlaydigan widget."""
from django import forms


class CropImageWidget(forms.ClearableFileInput):
    """Rasm tanlanganda brauzerda kesish oynasini ochadigan fayl maydoni.

    `ratio` — shu joy uchun tavsiya etilgan nisbat ("16/9" ko'rinishida).
    Foydalanuvchi rasmni surishi, kattalashtirishi yoki boshqa nisbat
    tanlashi mumkin; natija serverga allaqachon kesilgan holda keladi.
    """

    template_name = "widgets/crop_image.html"

    def __init__(self, attrs=None, ratio="16/9", ratio_label=None, max_width=1800):
        self.ratio = ratio
        self.ratio_label = ratio_label or ratio.replace("/", ":")
        self.max_width = max_width
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"].update(
            ratio=self.ratio,
            ratio_label=self.ratio_label,
            max_width=self.max_width,
        )
        return context

    class Media:
        css = {"all": ("css/cropper.css",)}
        js = ("js/cropper.js",)
