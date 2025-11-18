from django.db import models
from jalali.Jalalian import JDate

from base.models import Owner


class CreateMsg(models.Model):
    titel = models.CharField(max_length=200)
    info = models.TextField(blank=True,null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now=True)
    isreply = models.BooleanField(default=True)
    attach = models.FileField(blank=True,upload_to='msg/',default='0')
    orginal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titel

    def pdate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('j E')
        return newsdate

    def ptime(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('H:i')
        return newsdate


class ListMsg(models.Model):
    msg = models.ForeignKey(CreateMsg, on_delete=models.CASCADE)
    user = models.ForeignKey(Owner, on_delete=models.CASCADE)
    isread = models.BooleanField(default=False)
    tarikh = models.DateTimeField(blank=True,null=True)
    isremove = models.BooleanField(default=False)
    replyid=models.PositiveIntegerField( blank=True,null=True)
    star = models.BooleanField(default=False)
    orginal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.msg.titel

    def pdate(self):
        if self.tarikh:
            jd = JDate(self.tarikh.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('j E')
            return newsdate

    def ptime(self):
        if self.tarikh:
            jd = JDate(self.tarikh.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('H:i')
            return newsdate


class GroupOwners(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class GroupList(models.Model):
    groupowner = models.ForeignKey(GroupOwners, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    def __str__(self):
        return self.groupowner.name

