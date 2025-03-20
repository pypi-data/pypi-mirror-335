from typing import Any

from django.template import Library
from easy_thumbnails.files import get_thumbnailer

from crimsonslate_portfolio.models import Media

register = Library()


@register.inclusion_tag("portfolio/media/display.html")
def media_display(
    media: Media,
    css_class: str | None = None,
    force_image: bool = False,
    alias: str = "gallery",
) -> dict[str, Any]:
    options = {"size": (100, 100), "crop": True}
    return {
        "image": force_image if force_image else media.is_image,
        "class": css_class,
        "src": get_thumbnailer(media.source).get_thumbnail(options)
        if force_image and not media.is_image
        else media.source.url,
    }
