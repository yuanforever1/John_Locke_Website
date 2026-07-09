from django.contrib.auth.models import User
from django.db import models


def avatar_upload_to(instance, filename):
    return f"avatars/user_{instance.user_id}/{filename}"


class Profile(models.Model):
    """用户个人主页档案，与内置 User 一对一。"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    nickname = models.CharField("昵称", max_length=60, blank=True)
    avatar = models.ImageField(
        "头像", upload_to=avatar_upload_to, blank=True, null=True
    )
    bio = models.TextField("个人简介", blank=True)
    affiliation = models.CharField("机构 / 单位", max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "用户档案"
        verbose_name_plural = "用户档案"

    def __str__(self):
        return f"{self.nickname or self.user.username} 的档案"
