from django import template
from django.utils.safestring import mark_safe

from core.richtext import clean_html

register = template.Library()

UZ_MONTHS_FULL = (
    "yanvar", "fevral", "mart", "aprel", "may", "iyun",
    "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
)


@register.filter
def uzdate(value, fmt="long"):
    """Sanani o'zbekcha yozadi: 19-sentabr, 2026."""
    if not value:
        return ""
    month = UZ_MONTHS_FULL[value.month - 1]
    if fmt == "short":
        return f"{month} {value.year}"
    return f"{value.day}-{month}, {value.year}"


@register.filter
def richtext(value):
    """Saqlangan boy matnni chiqarishdan oldin yana bir bor tozalaydi."""
    return mark_safe(clean_html(value or ""))


@register.filter
def initials(value):
    parts = [p for p in str(value or "").split() if p]
    return "".join(p[0].upper() for p in parts[:2])


@register.filter
def is_checkbox(field):
    from django.forms import CheckboxInput

    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def is_richtext(field):
    from core.richtext import RichTextWidget

    return isinstance(field.field.widget, RichTextWidget)
