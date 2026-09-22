from django import forms

from core.forms import DateInput, StyledFormMixin
from core.richtext import RichTextFormField
from core.widgets import CropImageWidget

from .models import Article


class ArticleForm(StyledFormMixin, forms.ModelForm):
    body = RichTextFormField(label="Maqola matni")

    class Meta:
        model = Article
        fields = [
            "title", "rubric", "lead", "cover", "cover_caption", "body",
            "published_at", "slug", "is_published", "is_featured",
        ]
        widgets = {
            "lead": forms.Textarea(attrs={"rows": 2}),
            "published_at": DateInput(),
            "cover": CropImageWidget(ratio="16/9", ratio_label="16:9"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
