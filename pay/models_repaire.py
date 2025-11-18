import datetime
import jdatetime
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from jalali.Jalalian import JDate
from django.contrib.auth.models import User
from base.modelmanager import RoleeManager
from base.models import GsModel, Pump, Parametrs, Product, Owner, Storage, Zone
from .models import StatusRef, RepairStoreName, RepairRole
from django_jalali.db import models as jmodels
from django.conf import settings
from django.db import IntegrityError


_datetemplate = "%Y-%m-%d %H:%M:%S"
_shamsitemplate = 'l j E  Y'
_shamsitemplate2 = 'Y/m/d'


class Repaires(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    tarikh = models.DateField(auto_now_add=True)
    marsole = models.CharField(max_length=50, null=True, blank=True)
    marsole_send = models.DateField(null=True, blank=True)
    marsole_resid = models.DateField(null=True, blank=True)
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.zone.name

    def normal_date(self):
        jd = JDate(self.tarikh.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def normal_send(self):
        jd = JDate(self.marsole_send.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def normal_resid(self):
        jd = JDate(self.marsole_resid.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

def repair_post_save(sender, instance, created, *args, **kwargs):
    data = instance
    repairs = RepaireStores.objects.filter(store_id=data.id)
    for repair in repairs:
        repairrole = RepairRole.objects.get(storage_id=data.storage_id,repairstore_id=repair.repairstore_id)

        repairstore = RepaireStores.objects.filter(store__storage_id=data.storage_id, repairstore_id=repair.repairstore_id,
                                                   store__status_id=3).aggregate(
            tedad=Sum('amount'))
        if repairstore['tedad']:
            repairrole.inventory = repairstore['tedad']
        else:
            repairrole.inventory = 0
        repairstore2 = RepaireStores.objects.filter(store__storage_id=data.storage_id, repairstore_id=repair.repairstore_id,
                                                   store__status_id=2).aggregate(
            tedad=Sum('amount'))
        if repairstore2['tedad']:
            repairrole.ofroadvalue = repairstore2['tedad']
        else:
            repairrole.ofroadvalue = 0
        mojodi = (int(repairrole.inventory) + int(repairrole.ofroadvalue) + int(repairrole.startvalue))

        required = int(repairrole.usevalue) - mojodi if mojodi <= int(repairrole.usevalue) else 0
        repairrole.required=required
        repairrole.save()



post_save.connect(repair_post_save, sender=Repaires)


class RepaireStores(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Repaires, on_delete=models.CASCADE)
    repairstore = models.ForeignKey(RepairStoreName, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.store)

