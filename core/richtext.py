"""Boy matn (rich text) uchun tozalagich, widget va maydon."""
import re

import nh3
from django import forms
from django.utils.safestring import mark_safe

ALLOWED_TAGS = {
    "p", "br", "hr", "span", "div",
    "h2", "h3", "h4",
    "strong", "b", "em", "i", "u", "s", "sub", "sup",
    "ul", "ol", "li",
    "blockquote", "pre", "code",
    "a", "img", "figure", "figcaption",
    "table", "thead", "tbody", "tr", "th", "td",
    "iframe",
}

ALLOWED_ATTRIBUTES = {
    "*": {"class", "style"},
    "a": {"href", "title", "target", "class"},  # rel ni nh3 o'zi qo'shadi
    "img": {"src", "alt", "title", "width", "height", "class"},
    "iframe": {"src", "width", "height", "allowfullscreen", "frameborder", "class"},
    "ol": {"class", "start", "type"},
    "li": {"class", "data-list"},
    "td": {"colspan", "rowspan", "class"},
    "th": {"colspan", "rowspan", "class"},
}

ALLOWED_URL_SCHEMES = {"http", "https", "mailto", "tel"}

# style="" ichida faqat shu xossalarga ruxsat
ALLOWED_STYLE_PROPERTIES = {
    "text-align", "color", "background-color", "font-size", "font-weight",
    "font-style", "text-decoration", "padding-left", "margin-left",
}


def clean_html(value: str) -> str:
    """Foydalanuvchi kiritgan HTMLni xavfsiz holatga keltiradi."""
    if not value:
        return ""
    cleaned = nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer",
        strip_comments=True,
        clean_content_tags={"script", "style"},
        filter_style_properties=ALLOWED_STYLE_PROPERTIES,
    )
    if is_empty_html(cleaned):
        return ""
    return cleaned


def is_empty_html(value: str) -> bool:
    """Quill bo'sh bo'lganda “<p><br></p>” qaytaradi — shuni bo'sh deb hisoblaymiz."""
    if not value:
        return True
    stripped = re.sub(r"<(br|p|div|span)[^>]*>|</(p|div|span)>|&nbsp;|\s", "", value)
    return stripped == ""


class RichTextWidget(forms.Textarea):
    """Quill muharriri bilan bog'lanadigan yashirin textarea."""

    template_name = "widgets/richtext.html"

    def __init__(self, attrs=None, compact=False):
        default = {"class": "richtext-source", "rows": 12}
        if attrs:
            default.update(attrs)
        self.compact = compact
        super().__init__(default)

    def get_context(self, name, value, attrs):
        from django.conf import settings
        from django.urls import reverse

        context = super().get_context(name, value, attrs)
        context["widget"]["compact"] = self.compact
        context["widget"]["value_html"] = mark_safe(value or "")
        # Gemini kaliti berilgan bo'lsagina “tozalash” tugmasi chiqadi
        context["widget"]["assist"] = bool(getattr(settings, "GEMINI_API_KEY", ""))
        context["widget"]["assist_url"] = reverse("manage:assist_text")
        return context

    class Media:
        css = {"all": ("vendor/quill/quill.snow.css", "css/richtext.css", "css/cropper.css")}
        js = ("vendor/quill/quill.js", "js/cropper.js", "js/richtext.js")


class RichTextFormField(forms.CharField):
    widget = RichTextWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("strip", False)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = clean_html(super().clean(value))
        if self.required and not value:
            raise forms.ValidationError("Bu maydon to'ldirilishi shart.")
        return value
