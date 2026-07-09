"""
文件清理信号：当图片记录被删除或替换时，同步删除磁盘上的物理文件，
避免 media 目录中残留孤儿文件。

post_delete 在级联删除（如删除文件夹连带其图片）时也会对每个被删对象触发，
因此删除文件夹内的图片同样会清理文件。
"""
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import UserImage


@receiver(post_delete, sender=UserImage)
def delete_image_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=UserImage)
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = UserImage.objects.get(pk=instance.pk)
    except UserImage.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        old.image.delete(save=False)
