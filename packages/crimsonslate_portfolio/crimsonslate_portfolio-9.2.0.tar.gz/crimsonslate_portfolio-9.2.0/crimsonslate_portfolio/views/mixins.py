from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin, TemplateResponseMixin

if not hasattr(settings, "PORTFOLIO_PROFILE"):
    raise ImproperlyConfigured("'PORTFOLIO_PROFILE' setting is required.")


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    """A template mixin that enables htmx features."""

    partial_template_name: str | None = None
    """
    A partial template rendered by htmx.

    :type: :py:obj:`str` | :py:obj:`None`
    :value: :py:obj:`None`

    """

    def render_to_response(self, context: dict[str, Any], **response_kwargs):
        """
        Sets :py:attr:`template_name` to :py:attr:`partial_template_name` if it is present.

        The request must be an HTMX request and not `boosted`_.

        .. _boosted: https://htmx.org/attributes/hx-boost/
        """
        htmx_request = bool(self.request.headers.get("HX-Request"))
        boosted = bool(self.request.headers.get("HX-Boosted"))

        if htmx_request and self.partial_template_name and not boosted:
            self.template_name = self.partial_template_name
        return super().render_to_response(context, **response_kwargs)


class PortfolioProfileMixin(ContextMixin):
    """Adds :confval:`PORTFOLIO_PROFILE` to the view context."""

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = settings.PORTFOLIO_PROFILE
        return context
