from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField(max_length=500)
    keys = models.JSONField(unique=True)

    def __str__(self):
        return f"Subscription for {self.user.username}"


class Notification(models.Model):
    subject = models.CharField(max_length=80, verbose_name="تیتر پیام")
    info = models.TextField(verbose_name="شرح پیام")
    active = models.BooleanField(default=True, verbose_name="فعال")

    def __str__(self):
        return self.subject
