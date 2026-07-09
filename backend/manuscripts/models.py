from django.db import models


class Collection(models.Model):
    """系统提供的手稿集合，例如「法国旅行日记」。"""

    slug = models.SlugField("标识", max_length=80, unique=True)
    title = models.CharField("名称", max_length=160)
    subtitle = models.CharField("副标题", max_length=200, blank=True)
    description = models.TextField("简介", blank=True)
    period = models.CharField("时期", max_length=120, blank=True)
    language = models.CharField("语言", max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "手稿集"
        verbose_name_plural = "手稿集"
        ordering = ["slug"]

    def __str__(self):
        return self.title

    @property
    def page_count(self):
        return self.pages.count()


class ManuscriptPage(models.Model):
    """手稿集中的单页：包含图片与官方转写（ground truth）。"""

    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="pages"
    )
    page_number = models.PositiveIntegerField("页码", default=0)
    image_name = models.CharField("图片文件名", max_length=200)
    image = models.ImageField("手稿图片", upload_to="manuscripts/")
    transcription = models.TextField("官方转写", blank=True)

    class Meta:
        verbose_name = "手稿页"
        verbose_name_plural = "手稿页"
        ordering = ["collection", "page_number"]
        unique_together = ("collection", "image_name")

    def __str__(self):
        return f"{self.collection.slug} · 第 {self.page_number} 页"
