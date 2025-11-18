from django.db import models
from django.contrib.auth.models import User
from base.models import GsModel, Product, Owner
from django_jalali.db import models as jmodels


class DashboardConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gs_filter = models.ManyToManyField(GsModel, blank=True)
    date_range = models.CharField(max_length=20, default='7d')  # 7d, 30d, 90d, 1y
    refresh_rate = models.PositiveIntegerField(default=5)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dashboard Config - {self.user.username}"


class SavedReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    config = models.JSONField()  # ذخیره تنظیمات فیلترها
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DashboardView(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name