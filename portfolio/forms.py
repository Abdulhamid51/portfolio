from django import forms
from django.forms import inlineformset_factory

from core.forms import StyledFormMixin
from core.richtext import RichTextFormField
from core.widgets import CropImageWidget

from .models import Folder, Project, ProjectImage


class FolderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name", "slug", "description", "tone", "cover", "order"]
        help_texts = {"slug": "Bo'sh qoldirsangiz nomdan avtomatik yasaladi."}
        widgets = {"cover": CropImageWidget(ratio="3/2", ratio_label="3:2", max_width=1200)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


class ProjectForm(StyledFormMixin, forms.ModelForm):
    body = RichTextFormField(label="To'liq tavsif")

    class Meta:
        model = Project
        fields = [
            "title", "slug", "folder", "summary", "cover", "body",
            "role", "client", "tech", "year", "status",
            "live_url", "repo_url", "is_featured", "is_published", "order",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 2}),
            "cover": CropImageWidget(ratio="16/9", ratio_label="16:9"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["folder"].empty_label = "— papkasiz —"


class ProjectImageForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ["image", "caption", "order"]
        widgets = {"image": CropImageWidget(ratio="3/2", ratio_label="3:2", max_width=1600)}


ProjectImageFormSet = inlineformset_factory(
    Project, ProjectImage, form=ProjectImageForm, extra=2, can_delete=True,
)
