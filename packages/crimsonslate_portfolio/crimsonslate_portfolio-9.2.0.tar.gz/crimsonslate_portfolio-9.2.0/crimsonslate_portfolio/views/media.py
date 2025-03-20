from typing import Any

from django.db.models import QuerySet, Q
from django.views.generic import DetailView, TemplateView, ListView

from crimsonslate_portfolio.forms import MediaSearchForm
from crimsonslate_portfolio.models import Media, MediaTag
from crimsonslate_portfolio.views.mixins import (
    HtmxTemplateResponseMixin,
    PortfolioProfileMixin,
)


class MediaDetailView(HtmxTemplateResponseMixin, PortfolioProfileMixin, DetailView):
    http_method_names = ["get"]
    model = Media
    partial_template_name = "portfolio/media/partials/_detail.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().title
        return context


class MediaGalleryView(HtmxTemplateResponseMixin, PortfolioProfileMixin, ListView):
    allow_empty = True
    extra_context = {"title": "Gallery", "tags": MediaTag.objects.all()}
    http_method_names = ["get"]
    model = Media
    ordering = "date_created"
    paginate_by = 12
    partial_template_name = "portfolio/media/partials/_gallery.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/gallery.html"


class MediaSearchView(HtmxTemplateResponseMixin, PortfolioProfileMixin, TemplateView):
    extra_context = {"title": "Search", "tags": MediaTag.objects.all()}
    http_method_names = ["get"]
    partial_template_name = "portfolio/media/partials/_search.html"
    template_name = "portfolio/media/search.html"


class MediaSearchResultsView(
    HtmxTemplateResponseMixin, PortfolioProfileMixin, ListView
):
    allow_empty = True
    extra_context = {"title": "Search", "tags": MediaTag.objects.all()}
    http_method_names = ["get"]
    model = Media
    ordering = "title"
    paginate_by = 12
    partial_template_name = "portfolio/media/partials/_search_results.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/search_results.html"
    context_object_name = "search_results"

    def get_queryset(self) -> QuerySet:
        """Filters the queryset based on a query in an HTML request body."""
        queryset: QuerySet[Media, Media | None] = super().get_queryset()
        form: MediaSearchForm = MediaSearchForm({"q": self.request.GET.get("q")})
        query: str | None = form.cleaned_data["q"] if form.is_valid() else None

        return (
            queryset.filter(Q(title__startswith=query) | Q(title__iexact=query))
            if query is not None
            else queryset
        )
