import emoji as e

from django.core.validators import get_available_image_extensions
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from filer.fields.file import FilerFileField

from crimsonslate_portfolio.validators import validate_emoji


class MediaTag(models.Model):
    """Used to categorize :py:obj:`~crimsonslate_portfolio.models.Media` objects."""

    name = models.CharField(max_length=64)
    """A name for the tag."""
    emoji = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        validators=[validate_emoji],
    )
    """An emoji character."""

    class Meta:
        ordering = ["name"]
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self) -> str:
        return str(self.name)

    def save(self, **kwargs) -> None:
        """Encodes :py:attr:`emoji` before writing it to database."""
        if self.emoji:
            val = e.emojize(self.emoji)
            self.emoji = e.demojize(val) if e.is_emoji(val) else None
        super().save(**kwargs)

    def get_emoji_display(self) -> str:
        """Returns an emojizied string of :py:attr:`emoji`."""
        return e.emojize(self.emoji) if self.emoji else ""


class Media(models.Model):
    """A published work."""

    title = models.CharField(
        max_length=64,
        unique=True,
    )
    """A catchy title."""
    source = FilerFileField(
        related_name="source_media",
        on_delete=models.CASCADE,
    )
    """A source file."""
    subtitle = models.CharField(max_length=128, blank=True, null=True, default=None)
    """A medium-length subtitle."""
    desc = models.TextField(
        verbose_name="description", max_length=2048, blank=True, null=True, default=None
    )
    """A lengthy description."""
    slug = models.SlugField(
        max_length=64, unique=True, blank=True, null=True, default=None
    )
    """A programatically generated slug."""
    is_hidden = models.BooleanField(default=False)
    """Whether or not the media is hidden."""
    is_image = models.BooleanField(blank=True, null=True, editable=False)
    """Whether or not the media is an image."""
    tags = models.ManyToManyField(
        "crimsonslate_portfolio.MediaTag", default=None, blank=True
    )
    """Tags assigned to the media."""

    date_created = models.DateTimeField(default=timezone.now)
    """Date and time the media was created."""
    date_published = models.DateTimeField(default=timezone.now, editable=False)
    """Date and time the media was published."""

    def __str__(self) -> str:
        """Returns the media title."""
        return str(self.title)

    def save(self, **kwargs) -> None:
        """Sets :py:attr:`is_image` and generates a slug for the media."""
        self.is_image = self.file_extension in get_available_image_extensions()
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the media's detail view."""
        return reverse("detail media", kwargs={"slug": self.slug})

    @property
    def file_extension(self) -> str:
        """Naively determined file extension for the media source file."""
        return self.source.file.name.split(".")[-1]
