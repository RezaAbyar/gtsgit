from django.db import models
from django.db.models.signals import post_save
from jalali.Jalalian import JDate
from django.contrib.auth.models import User
from django.db import IntegrityError
from base.models import Zone, GsModel, Pump, Owner, Ticket
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
import os

_datetemplate = "%Y-%m-%d %H:%M:%S"
_shamsitemplate = 'l j E  Y'
_shamsitemplate2 = 'Y/m/d'


class Status(models.Model):
    info = models.CharField(max_length=50)

    def __str__(self):
        return self.info


class Seris(models.Model):
    info = models.CharField(max_length=50)

    def __str__(self):
        return self.info


class Peymankar(models.Model):
    name = models.CharField(max_length=50)
    date_in = models.DateField()
    date_out = models.DateField()
    active = models.BooleanField(default=True)
    ename = models.CharField(max_length=10, blank=True, null=True, default='smart')

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=100)
    ename = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class InsertLock(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    peymankar = models.ForeignKey(Peymankar, on_delete=models.CASCADE)
    seri = models.ForeignKey(Seris, on_delete=models.CASCADE)
    serial_in = models.PositiveIntegerField()
    serial_out = models.PositiveIntegerField()
    tarikh = models.DateField()
    tedad = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, blank=True, null=True)
    resid = models.BooleanField(default=False)

    def __str__(self):
        return self.zone.name

    def pdate(self):
        jd = JDate(self.tarikh.strftime(_datetemplate))
        newsdate = jd.format('Y/m/j ')
        return newsdate


def insertlock_post_save(sender, instance, created, *args, **kwargs):
    data = instance
    if created:
        bulk_list = list()
        serial_out = int(data.serial_out) + 1
        for item in range(int(data.serial_in), int(serial_out)):
            lenserial = len(data.serial_out)
            _len = lenserial - len(str(item))
            _zero = ''
            for i in range(_len):
                _zero = str(_zero) + '0'
            _serial = str(_zero) + str(item)
            LockModel.objects.filter(serial=str(data.seri.info) + str(_serial), status_id__in=[6, 10, 9]).delete()
            bulk_list.append(
                LockModel(zone_id=data.zone_id, input_date_unit=data.tarikh, ename=data.peymankar.ename,
                          idu_user_id=data.user.id, seri_id=data.seri.id, serial=str(data.seri.info) + str(_serial),
                          serial_number=int(item), status_id=3, insertlock_id=data.id)
            )
        try:
            LockModel.objects.bulk_create(bulk_list)
        except IntegrityError:
            return False


post_save.connect(insertlock_post_save, sender=InsertLock)


class SendPoshtiban(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    tarikh = models.DateField()
    seri = models.ForeignKey(Seris, on_delete=models.CASCADE)
    serial_in = models.CharField(max_length=10)
    serial_out = models.CharField(max_length=10)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    tedad = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resid = models.BooleanField(default=False)
    ename = models.CharField(max_length=10, null=True, blank=True, default='smart')

    def __str__(self):
        return self.zone.name

    def pdate(self):
        jd = JDate(self.tarikh.strftime(_datetemplate))
        newsdate = jd.format('Y/m/j ')
        return newsdate


def sendposhtiban_post_save(sender, instance, created, *args, **kwargs):
    data = instance
    serial_out = int(data.serial_out) + 1
    for item in range(int(data.serial_in), int(serial_out)):
        lenserial = len(data.serial_out)
        _len = lenserial - len(str(item))
        _zero = ''
        for i in range(_len):
            _zero = str(_zero) + '0'
        _serial = str(_zero) + str(item)

        try:
            if not data.resid:
                lockmodel = LockModel.objects.get(serial=str(data.seri.info) + str(_serial), status_id__in=[3, 4, 7])
                lockmodel.send_date_poshtiban = data.tarikh
                lockmodel.sdp_user_id = data.user.id
                lockmodel.status_id = 4
                lockmodel.sendposhtiban_id = data.id
                lockmodel.owner_id = data.owner_id
                lockmodel.save()

        except:
            pass


post_save.connect(sendposhtiban_post_save, sender=SendPoshtiban)


class GetLockPeymankar(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    peymankar = models.ForeignKey(Peymankar, on_delete=models.CASCADE)
    tedad = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    resid = models.BooleanField(default=False)
    ename = models.CharField(max_length=10, null=True, blank=True, default='smart')

    def __str__(self):
        return self.zone.name

    def pdate(self):
        jd = JDate(self.created_at.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate


def validate_no_spaces(value):
    if ' ' in value:
        raise ValidationError(
            _('فاصله (Space) در این فیلد مجاز نیست.'),
            code='invalid'
        )


class LockModel(models.Model):
    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"

        filename = f"{unique_id}.{ext}"
        return os.path.join("soratjalasepolomb/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 500
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 500
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    meeting_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="شماره صورتجلسه"
    )
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    seri = models.ForeignKey(Seris, on_delete=models.CASCADE, null=True, blank=True, db_index=True)

    serial = models.CharField(max_length=10, unique=True, db_index=True, validators=[validate_no_spaces])
    serial_number = models.PositiveIntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    input_date_setad = models.DateField(null=True, blank=True)
    ids_username = models.CharField(max_length=50, null=True, blank=True)

    input_date_anbar = models.DateField(null=True, blank=True)
    ida_username = models.CharField(max_length=50, null=True, blank=True)

    input_date_unit = models.DateField(null=True, blank=True)
    idu_username = models.CharField(max_length=50, null=True, blank=True)
    insertlock = models.ForeignKey(InsertLock, on_delete=models.CASCADE, null=True, blank=True)

    send_date_poshtiban = models.DateField(null=True, blank=True)
    sdp_username = models.CharField(max_length=50, null=True, blank=True)
    sendposhtiban = models.ForeignKey(SendPoshtiban, on_delete=models.CASCADE, null=True, blank=True)

    send_date_tek = models.DateField(null=True, blank=True)
    sdt_username = models.CharField(max_length=50, null=True, blank=True)

    send_date_gs = models.DateField(null=True, blank=True)
    sdg_username = models.CharField(max_length=50, null=True, blank=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, null=True, blank=True)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE, null=True, blank=True)

    input_date_gs = models.DateField(null=True, blank=True)
    idg_username = models.CharField(max_length=50, null=True, blank=True)

    input_date_tek = models.DateField(null=True, blank=True)
    idt_username = models.CharField(max_length=50, null=True, blank=True)

    input_date_poshtiban = models.DateField(null=True, blank=True)
    idp_username = models.CharField(max_length=50, null=True, blank=True)

    send_date_emha = models.DateField(null=True, blank=True)
    sde_username = models.CharField(max_length=50, null=True, blank=True)

    resid_date_unit = models.DateField(null=True, blank=True)
    resid_date_tek = models.DateField(null=True, blank=True)

    ids_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='setad_locks')
    ida_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='anbar_locks')
    idu_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='unit_locks')
    sdp_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='poshtiban_send_locks')
    sdt_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tek_send_locks')
    sdg_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='gs_send_locks')
    idg_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='gs_input_locks')
    idt_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tek_input_locks')
    idp_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='poshtiban_input_locks')
    sde_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='emha_send_locks')
    rdu_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='resid_unit_locks')
    rdt_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='resid_tek_locks')

    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket_list')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    getlockpeymankar = models.ForeignKey(GetLockPeymankar, on_delete=models.CASCADE, null=True, blank=True)
    ticket2 = models.PositiveIntegerField(null=True, blank=True)
    manualadd = models.PositiveIntegerField(null=True, blank=True)
    ename = models.CharField(max_length=10, null=True, blank=True, default='smart')
    description = models.CharField(max_length=500, null=True, blank=True)
    soratjalase = models.ImageField(upload_to=wrapper, blank=True, null=True, validators=[validate_image],
                                    verbose_name="فایل صورتجلسه")

    def __str__(self):
        return self.serial

    def pdate(self):
        jd = JDate(self.updated.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate

    def installdate(self):
        newsdate = ""
        if self.send_date_gs:
            jd = JDate(self.send_date_gs.strftime(_datetemplate))
            newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def fakdate(self):
        newsdate = ""
        if self.input_date_gs:
            jd = JDate(self.input_date_gs.strftime(_datetemplate))
            newsdate = jd.format(_shamsitemplate2)

        return newsdate


@receiver(pre_save, sender=LockModel)
def remove_spaces_from_serial(sender, instance, **kwargs):
    if hasattr(instance, 'serial'):
        instance.serial = instance.serial.replace(' ', '')


class LockLogs(models.Model):
    lockmodel = models.ForeignKey(LockModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, null=True, blank=True)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    info = models.CharField(max_length=110, blank=True, null=True)

    def __str__(self):
        return self.lockmodel.serial

    def pdatetime(self):
        jd = JDate(self.created_at.strftime(_datetemplate))
        newsdate = jd.format('l j E  Y -  H:i')
        return newsdate


def log_product_update(sender, instance, created, **kwargs):
    _owner = None

    if instance.status_id == 1:
        _owner = instance.ids_user_id
    elif instance.status_id == 2:
        _owner = instance.ida_user_id
    elif instance.status_id == 3:
        _owner = instance.idu_user_id
    elif instance.status_id == 4:
        _owner = instance.sdp_user_id
    elif instance.status_id == 5:
        _owner = instance.idg_user_id
    elif instance.status_id == 6:
        _owner = instance.idp_user_id
    if _owner is not None:
        LockLogs.objects.create(
            status_id=instance.status_id,
            owner_id=_owner,
            position_id=instance.position_id,
            lockmodel_id=instance.id,
            gs_id=instance.gs_id,
            pump_id=instance.pump_id)


post_save.connect(log_product_update, sender=LockModel)
