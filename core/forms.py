import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    Award, Education, Experience, LanguageSkill, Message, Profile, Skill,
    SkillGroup, SlideItem, SocialLink,
)
from .richtext import RichTextFormField, RichTextWidget
from .widgets import CropImageWidget


# Ko'rinmaydigan boshqaruv belgilari (sarlavha/log ichiga nimadir qistirishga urinish)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\u2028\u2029]")


def clean_line(value, label, required=True):
    """Bir qatorlik matnni tozalaydi: yangi qator va boshqaruv belgilari olib tashlanadi."""
    value = CONTROL_CHARS.sub("", (value or "")).replace("\n", " ").replace("\r", " ")
    value = " ".join(value.split())
    if required and not value:
        raise forms.ValidationError(f"{label} to'ldirilishi shart.")
    return value


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, format="%Y-%m-%d")


class StyledFormMixin:
    """Barcha maydonlarga umumiy CSS sinflarini qo'shadi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, RichTextWidget):
                continue
            css = widget.attrs.get("class", "")
            if "f-range" in css:
                continue
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = (css + " f-check").strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (css + " f-select").strip()
            elif isinstance(widget, (forms.ClearableFileInput, forms.FileInput)):
                widget.attrs["class"] = (css + " f-file").strip()
            else:
                widget.attrs["class"] = (css + " f-input").strip()
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 4)


class ProfileForm(StyledFormMixin, forms.ModelForm):
    about = RichTextFormField(label="Men haqimda")

    class Meta:
        model = Profile
        fields = [
            "full_name", "headline", "tagline", "about", "location", "email",
            "phone", "website", "photo", "resume_file", "available_for_work",
            "masthead", "edition_note", "footer_note",
        ]
        widgets = {
            "photo": CropImageWidget(ratio="1/1", ratio_label="1:1", max_width=900),
        }


class SocialLinkForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ["label", "handle", "url", "order"]


class ExperienceForm(StyledFormMixin, forms.ModelForm):
    description = RichTextFormField(label="Tavsif")

    class Meta:
        model = Experience
        fields = [
            "role", "company", "company_url", "location",
            "start_date", "end_date", "is_current", "description", "order",
        ]
        widgets = {"start_date": DateInput(), "end_date": DateInput()}

    def clean(self):
        data = super().clean()
        if data.get("is_current"):
            data["end_date"] = None
        start, end = data.get("start_date"), data.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Tugash sanasi boshlanishdan oldin bo'lmasligi kerak.")
        return data


class EducationForm(StyledFormMixin, forms.ModelForm):
    description = RichTextFormField(label="Tavsif")

    class Meta:
        model = Education
        fields = [
            "degree", "institution", "location",
            "start_date", "end_date", "is_current", "description", "order",
        ]
        widgets = {"start_date": DateInput(), "end_date": DateInput()}

    clean = ExperienceForm.clean


class SkillGroupForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SkillGroup
        fields = ["name", "order"]


class SkillForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["group", "name", "note", "order"]


class AwardForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Award
        fields = ["title", "issuer", "date", "url", "description", "order"]
        widgets = {"date": DateInput(), "description": forms.Textarea(attrs={"rows": 3})}


class LanguageSkillForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LanguageSkill
        fields = ["name", "level", "order"]


def _range(min_value, max_value, unit=""):
    return forms.NumberInput(attrs={
        "type": "range", "min": min_value, "max": max_value, "step": 1,
        "class": "f-range", "data-unit": unit,
    })


class SlideItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SlideItem
        fields = [
            "title", "subtitle", "image", "url", "link_label",
            "side", "panel_style", "panel_blur", "image_blur", "blur_width",
            "is_active", "order",
        ]
        widgets = {
            "image": CropImageWidget(ratio="21/9", ratio_label="21:9", max_width=2200),
            "panel_blur": _range(0, 40, "px"),
            "image_blur": _range(0, 40, "px"),
            "blur_width": _range(15, 100, "%"),
        }

    def clean_url(self):
        url = (self.cleaned_data.get("url") or "").strip()
        if url and not url.startswith(("/", "http://", "https://", "mailto:", "tel:")):
            raise forms.ValidationError(
                "Havola “/” bilan boshlanadigan ichki yo'l yoki https:// manzil bo'lsin."
            )
        return url


class MessageForm(StyledFormMixin, forms.ModelForm):
    """Ommaviy aloqa shakli."""

    MESSAGE_MAX = 500

    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    body = forms.CharField(
        label="Xabar",
        max_length=MESSAGE_MAX,
        widget=forms.Textarea(attrs={
            "rows": 6,
            "maxlength": MESSAGE_MAX,
            "placeholder": "Xabaringiz…",
        }),
    )

    class Meta:
        model = Message
        fields = ["name", "contact", "subject", "body"]
        widgets = {
            "contact": forms.TextInput(attrs={
                "placeholder": "+998 90 123 45 67, @username yoki pochta@misol.uz",
                "autocomplete": "off",
            }),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spamga o'xshaydi.")
        return ""

    def clean_name(self):
        return clean_line(self.cleaned_data.get("name"), "Ism")

    def clean_contact(self):
        value = clean_line(self.cleaned_data.get("contact"), "Bog'lanish ma'lumoti")
        if len(value) < 4:
            raise forms.ValidationError("Kamida 4 ta belgi yozing.")
        return value

    def clean_subject(self):
        return clean_line(self.cleaned_data.get("subject"), "Mavzu", required=False)

    def clean_body(self):
        value = CONTROL_CHARS.sub("", (self.cleaned_data.get("body") or "").strip())
        if len(value) < 5:
            raise forms.ValidationError("Xabar juda qisqa.")
        if len(value) > self.MESSAGE_MAX:
            raise forms.ValidationError(
                f"Xabar {self.MESSAGE_MAX} belgidan oshmasligi kerak."
            )
        return value


class StyledLoginForm(StyledFormMixin, AuthenticationForm):
    """Sayt uslubiga mos kirish shakli."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Foydalanuvchi nomi yoki parol noto'g'ri.",
        "inactive": "Bu hisob faol emas.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Foydalanuvchi nomi"
        self.fields["password"].label = "Parol"
