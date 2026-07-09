from django.contrib import admin

from .models import Collection, ManuscriptPage


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "period", "page_count")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ManuscriptPage)
class ManuscriptPageAdmin(admin.ModelAdmin):
    list_display = ("collection", "page_number", "image_name")
    list_filter = ("collection",)
    search_fields = ("image_name", "transcription")
