from django.contrib.auth.models import User
from django.db import models


def user_image_upload_to(instance, filename):
    return f"workspace/user_{instance.owner_id}/{filename}"


class Folder(models.Model):
    """用户工作区中的文件夹，支持多级嵌套。"""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders"
    )
    name = models.CharField("名称", max_length=120)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "工作区文件夹"
        verbose_name_plural = "工作区文件夹"
        ordering = ["name"]
        unique_together = ("owner", "parent", "name")

    def __str__(self):
        return f"{self.owner.username} / {self.name}"


class UserImage(models.Model):
    """用户上传到工作区的手稿图片。"""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="images"
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
    )
    image = models.ImageField("图片", upload_to=user_image_upload_to)
    original_name = models.CharField("原始文件名", max_length=200, blank=True)
    size = models.PositiveIntegerField("字节大小", default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "工作区图片"
        verbose_name_plural = "工作区图片"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name or f"图片 #{self.pk}"


class Recognition(models.Model):
    """一张工作区图片的 Agnes 识别结果。"""

    class Status(models.TextChoices):
        PENDING = "pending", "待识别"
        PROCESSING = "processing", "识别中"
        DONE = "done", "已完成"
        FAILED = "failed", "失败"

    image = models.OneToOneField(
        UserImage, on_delete=models.CASCADE, related_name="recognition"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    text = models.TextField("识别文本", blank=True)
    model_name = models.CharField("使用模型", max_length=120, blank=True)
    error = models.TextField("错误信息", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "识别结果"
        verbose_name_plural = "识别结果"

    def __str__(self):
        return f"识别 · {self.image} · {self.get_status_display()}"
