from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("gallery/", views.MediaGalleryView.as_view(), name="gallery"),
    path("search/", views.MediaSearchView.as_view(), name="search"),
    path(
        "search/results/", views.MediaSearchResultsView.as_view(), name="search results"
    ),
    path("<str:slug>/", views.MediaDetailView.as_view(), name="detail media"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
