from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from crimsonslate_portfolio.forms import PortfolioAuthenticationForm
from crimsonslate_portfolio.views.mixins import (
    HtmxTemplateResponseMixin,
    PortfolioProfileMixin,
)


class ContactView(PortfolioProfileMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact"}
    http_method_names = ["get"]
    partial_template_name = "portfolio/partials/_contact.html"
    template_name = "portfolio/contact.html"


class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {"title": "Login"}
    form_class = PortfolioAuthenticationForm
    http_method_names = ["get", "post"]
    partial_template_name = "portfolio/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("gallery")
    template_name = "portfolio/login.html"


class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    partial_template_name = "portfolio/partials/_logout.html"
    success_url = reverse_lazy("gallery")
    template_name = "portfolio/logout.html"
