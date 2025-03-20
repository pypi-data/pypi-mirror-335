from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crimsonslate_portfolio.models import Media


class PortfolioAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].widget.attrs.update(
                {"class": "p-2 rounded bg-white", "placeholder": name.title()}
            )


class MediaSearchForm(forms.Form):
    q = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={"class": "p-2 rounded bg-white", "placeholder": "Search..."}
        ),
    )


class MediaCreateForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = [
            "source",
            "title",
            "subtitle",
            "desc",
            "is_hidden",
            "tags",
            "date_created",
        ]

    def __init__(self, field_class: str | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.field_class = field_class or "p-2 bg-white rounded border border-gray-600"
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({"class": self.field_class})


class MediaUpdateForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = [
            "source",
            "title",
            "subtitle",
            "desc",
            "is_hidden",
            "tags",
            "date_created",
        ]

    def __init__(self, field_class: str | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.field_class = field_class or "p-2 bg-white rounded border border-gray-600"
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({"class": self.field_class})
