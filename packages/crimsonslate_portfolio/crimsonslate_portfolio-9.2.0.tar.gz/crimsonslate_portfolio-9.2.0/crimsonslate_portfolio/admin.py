from django.contrib import admin

from .models import Media, MediaTag


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    date_hierarchy = "date_created"
    fieldsets = [
        ("Files", {"fields": ["source", "thumb"]}),
        ("Data", {"fields": ["title", "subtitle", "desc", "slug", "is_image", "tags"]}),
        ("Dates", {"fields": ["date_created", "date_published"]}),
        ("Settings", {"fields": ["is_hidden"]}),
    ]
    readonly_fields = ["slug", "is_image", "date_published"]


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    list_display = ["get_emoji_display", "name"]
    list_display_links = ["name"]
