from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "affiliation", "updated_at")
    search_fields = ("user__username", "nickname", "user__email")
