from django.db import models
from jalali.Jalalian import JDate

from base.models import Owner


class Captcha(models.Model):
    number = models.CharField(max_length=7)
    img = models.ImageField(upload_to='captcha/')

    def __int__(self):
        return self.number


class VisitManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('logdb')


class Visits(models.Model):
    SERVER_PORT = models.CharField(max_length=8, blank=True)
    REQUEST_METHOD = models.CharField(max_length=40, blank=True)
    SERVER_NAME = models.CharField(max_length=90, blank=True)
    REMOTE_USER = models.CharField(max_length=40, blank=True)
    REMOTE_HOST = models.CharField(max_length=20, blank=True)
    REMOTE_ADDR = models.CharField(max_length=17, blank=True)
    QUERY_STRING = models.TextField(blank=True)
    HTTP_HOST = models.CharField(max_length=50, blank=True)
    HTTP_REFERER = models.TextField(blank=True)
    create = models.DateTimeField(auto_now_add=True, blank=True)
    objects = VisitManager()

    def __str__(self):
        return self.REMOTE_ADDR

    class Meta:
        verbose_name = 'اطلاعات صفحه',
        verbose_name_plural = 'صفحات مشاهده شده'


class Logs(models.Model):
    create = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    parametr1 = models.TextField()
    parametr2 = models.TextField()
    gs = models.PositiveIntegerField(null=True, blank=True)
    macaddress = models.CharField(max_length=50, null=True, blank=True, default='0')

    def __str__(self):
        return self.owner.name + " " + self.owner.lname

    class Meta:
        verbose_name = 'رویداد کاربران',
        verbose_name_plural = 'رویداد کاربران'
        indexes = [
            models.Index(fields=['gs']),
            models.Index(fields=['-create']),
        ]

    def pdate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d H:i')
        return newsdate



