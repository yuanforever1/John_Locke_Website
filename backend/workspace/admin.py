from django.contrib import admin

from .models import Folder, Recognition, UserImage


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "parent", "created_at")
    list_filter = ("owner",)


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "folder", "uploaded_at")
    list_filter = ("owner",)


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ("image", "status", "model_name", "updated_at")
    list_filter = ("status",)
