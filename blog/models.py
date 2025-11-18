from django.db import models
from django.db.models.signals import post_save
from jalali.Jalalian import JDate

from base.models import Owner, Role

_datetemplate = "%Y-%m-%d %H:%M:%S"
_shamsitemplate = 'E  Y'
_shamsitemplate2 = 'Y/m/d'


class VideoProvider(models.Model):
    name = models.CharField(max_length=20)
    en = models.CharField(max_length=800, null=True, blank=True)

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=20)
    en = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Videos(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tags)
    video_url = models.TextField(blank=True, null=True)
    views = models.IntegerField(default=0)
    image = models.ImageField(upload_to='learning/')
    video_provider = models.ForeignKey(VideoProvider, on_delete=models.CASCADE, blank=True, null=True)
    role = models.ManyToManyField(Role)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    sort = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title

    def normal_date(self):
        jd = JDate(self.created.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate
