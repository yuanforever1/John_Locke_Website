from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    """每创建一个用户，自动为其建立档案。"""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_delete, sender=Profile)
def delete_avatar_on_delete(sender, instance, **kwargs):
    """删除用户（档案随之删除）时，清理其头像文件。"""
    if instance.avatar:
        instance.avatar.delete(save=False)


@receiver(pre_save, sender=Profile)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """更换头像时，删除旧头像文件。"""
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
    if old.avatar and old.avatar != instance.avatar:
        old.avatar.delete(save=False)
