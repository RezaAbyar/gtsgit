import datetime
import os
import jdatetime
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models import Sum
from jalali.Jalalian import JDate
from django.contrib.auth.models import User
from base.modelmanager import RoleeManager
from base.models import GsModel, Pump, Parametrs, Product, Owner, Zone
from django_jalali.db import models as jmodels
from cryptography.fernet import Fernet
from django.conf import settings
from django.db import IntegrityError
from api.samplekey import decrypt
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django_jalali.db import models as jmodels


def to_jalali(gregorian_date):
    """Convert a Gregorian date to Jalali format."""
    try:
        return JDate.fromgregorian(date=gregorian_date).strftime('%Y/%m/%d')
    except Exception:
        return 'غیر قابل خوانش'


class SellModel(models.Model):
    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"

        filename = f"{unique_id}.{ext}"
        return os.path.join("sell/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 500
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 500
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, related_name='gs_sell', db_index=True)
    tolombeinfo = models.ForeignKey(Pump, on_delete=models.CASCADE, db_index=True)
    pumpnumber = models.PositiveIntegerField(blank=True)
    start = models.PositiveIntegerField(default=0)
    end = models.PositiveIntegerField(default=0)
    sell = models.PositiveIntegerField(blank=True)
    yarane = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    nimeyarane = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azad1 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azad2 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azad = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    ezterari = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    haveleh = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azmayesh = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    sellkol = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    ekhtelaf = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    mojaz = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    nomojaz = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    nomojaz2 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    tarikh = jmodels.jDateField(db_index=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    dore = models.CharField(max_length=204, null=True, blank=True)
    uniq = models.CharField(max_length=25, unique=True, blank=True)
    iscrash = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    information = models.TextField(null=True, blank=True)
    electronics = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    mindatecheck = models.CharField(max_length=50, null=True, blank=True)
    islocked = models.BooleanField(default=False)
    mogh = models.PositiveIntegerField(default=0)
    moghnumber = models.PositiveIntegerField(default=0)
    t_start = models.PositiveIntegerField(default=0)
    t_end = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=wrapper, blank=True, null=True, validators=[validate_image])
    is_soratjalase = models.BooleanField(default=False)
    is_change_counter = models.BooleanField(default=False)
    crashdate = models.ForeignKey("SellTime", null=True, blank=True, on_delete=models.SET_NULL)

    object_role = RoleeManager()
    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['tarikh', 'product']),
            models.Index(fields=['gs', 'tarikh', 'product']),
            models.Index(fields=['iscrash', '-tarikh']),
            models.Index(fields=['gs', 'iscrash', '-tarikh']),

        ]

    def __str__(self):
        return self.gs.name

    def clean(self):
        """Validate sale data."""
        if self.sell < 0 or self.yarane < 0 or self.azad < 0:
            raise ValidationError("Sales values cannot be negative.")

    def electronics(self):
        return self.sellkol - self.azmayesh

    @property
    def is_approved_discrepancy(self):
        return self.discrepancies.filter(status='system_approved').exists()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.is_change_counter = self.t_start != 0
        if self.image:
            self.is_soratjalase = True
        self.sell = self.sell or 0
        try:
            self.ekhtelaf = abs(float(self.sellkol) - float(self.sell))
            self.mojaz = round((self.sell * 0.5) / 1000, 2)
            self.nomojaz = self.nomojaz2 = abs(self.ekhtelaf - self.mojaz)
            if self.mojaz >= self.ekhtelaf:
                self.nomojaz = self.nomojaz2 = 0

            sell = InfoEkhtelafLogs.objects.filter(pomp_id=self.tolombeinfo_id, amount__gte=0, tarikh=self.tarikh)
            if sell.count() > 0:
                sell = sell.first()
                self.nomojaz = sell.amount
                sell.save()
        except:
            print('err')

        super().save(force_insert, force_update, *args, **kwargs)


class Mojodi(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    tarikh = jmodels.jDateField(db_index=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    benzin = models.PositiveIntegerField(default=0)
    super = models.PositiveIntegerField(default=0)
    gaz = models.PositiveIntegerField(default=0)
    uniq = models.CharField(max_length=15, unique=True)
    darsadbenzin = models.PositiveIntegerField(default=0)
    darsadsuper = models.PositiveIntegerField(default=0)
    darsadgaz = models.PositiveIntegerField(default=0)
    sending = models.PositiveIntegerField(default=0)
    sendinggaz = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.gs.name

    object_role = RoleeManager()
    objects = models.Manager()

    def darsadbenzin(self):
        try:
            benzin = round((self.benzin / self.gs.m_benzin) * 100) if self.benzin != 0 else 0
        except ZeroDivisionError:
            benzin = 0
        except TypeError:
            benzin = 0
        return benzin

    def darsadsuper(self):
        try:
            _super = round((self.super / self.gs.m_super) * 100) if self.super != 0 else 0
        except ZeroDivisionError:
            _super = 0
        except TypeError:
            _super = 0
        return _super

    def darsadgaz(self):
        try:
            gaz = round((self.gaz / self.gs.m_naftgaz) * 100) if self.gaz != 0 else 0
        except ZeroDivisionError:
            gaz = 0
        except TypeError:
            gaz = 0
        return gaz


class IpcLog(models.Model):
    gs = models.ForeignKey(GsModel, null=True, blank=True, on_delete=models.CASCADE, related_name='gsipclog',
                           db_index=True)
    gsid = models.CharField(max_length=150, blank=True)
    dore = models.PositiveIntegerField(db_index=True, blank=True)
    date_ipc = models.CharField(max_length=10, blank=True)
    time_ipc = models.CharField(max_length=10, blank=True)
    dashboard_version = models.CharField(max_length=20, blank=True)
    rpm_version = models.CharField(max_length=150, blank=True)
    rpm_version_date = models.CharField(max_length=200, blank=True)
    pt_version = models.CharField(max_length=150, blank=True)
    quta_table_version = models.CharField(max_length=150, blank=True)
    zone_table_version = models.CharField(max_length=150, blank=True)
    price_table_version = models.CharField(max_length=150, blank=True)
    blacklist_version = models.CharField(max_length=150, blank=True)
    last_connection = models.CharField(max_length=150, blank=True)
    blacklist_count = models.CharField(max_length=150, blank=True)
    hd_serial = models.CharField(max_length=170, blank=True)
    os_version = models.CharField(max_length=150, blank=True)
    bl_ipc = models.CharField(max_length=150, null=True, blank=True)
    modemname = models.CharField(max_length=10, blank=True, null=True)
    sam = models.BooleanField(default=False)
    modem = models.BooleanField(default=False)
    poler = models.BooleanField(default=False)
    datacenter = models.BooleanField(default=False)
    fasb = models.BooleanField(default=False)
    asmelat = models.BooleanField(default=False)
    mellatmodem = models.BooleanField(default=False)
    internet = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    uniq = models.CharField(max_length=20, unique=True, blank=True)
    contradiction = models.BooleanField(default=False)
    updatedate = models.DateTimeField(null=True, blank=True)
    ck_rpm_version = models.BooleanField(default=False)
    ck_dashboard_version = models.BooleanField(default=False)
    ck_pt_version = models.BooleanField(default=False)
    ck_pt_online = models.BooleanField(default=False)
    ck_quta_table_version = models.BooleanField(default=False)
    ck_price_table_version = models.BooleanField(default=False)
    ck_zone_table_version = models.BooleanField(default=False)
    ck_blacklist_version = models.BooleanField(default=False)
    ck_blacklist_count = models.BooleanField(default=False)
    imagever = models.CharField(max_length=10, default='0', blank=True)
    gs_version = models.CharField(max_length=10, default='0', blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.gs.name

    def gsid_decode(self):

        result = decrypt(self.gsid)
        self.gsid = result
        self.save()
        return result

    def rpm_decode(self):
        result = decrypt(self.rpm_version)
        self.rpm_version = result
        self.save()
        return result

    def pt_decode(self):
        result = decrypt(self.pt_version)
        self.pt_version = result
        self.save()
        return result

    def quta_table_version_decode(self):
        result = decrypt(self.quta_table_version)
        self.quta_table_version = result
        self.save()
        return result

    def price_table_version_decode(self):
        result = decrypt(self.price_table_version)
        self.price_table_version = result
        self.save()
        return result

    def blacklist_version_decode(self):
        result = decrypt(self.blacklist_version)
        self.blacklist_version = result
        self.save()
        return result

    def blacklist_count_decode(self):
        result = decrypt(self.blacklist_count)
        self.blacklist_count = result
        self.save()
        return result

    def zone_table_version_decode(self):
        result = decrypt(self.zone_table_version)
        self.zone_table_version = result
        self.save()
        return result

    def last_connection_decode(self):
        result = decrypt(self.last_connection)
        self.last_connection = result
        self.save()
        return result

    def os_version_decode(self):
        result = decrypt(self.os_version)
        self.os_version = result
        self.save()
        return result

    def bl_ipc_decode(self):
        result = decrypt(self.bl_ipc)
        self.bl_ipc = result
        self.save()
        return result

    def ipcdate(self):
        dt = self.date_ipc.split("-")
        if len(self.date_ipc) > 5:
            datein = datetime.date(day=int(dt[2]), month=int(dt[1]), year=int(dt[0]))
            jd = JDate(datein.strftime("%Y-%m-%d"))
            try:
                newsdate = jd.format('Y/m/d')
            except:
                return 'غیر قابل خوانش'
            return newsdate
        return "ثبت نشده"

    def diffdate(self):
        now = self.updatedate
        if len(self.date_ipc) > 5:
            dt = self.date_ipc.split("-")
            st = self.time_ipc.split(":")
            old = datetime.datetime(day=int(dt[2]), month=int(dt[1]), year=int(dt[0]), hour=int(st[0]),
                                    minute=int(st[1]), second=1)
            now = datetime.datetime(day=now.day, month=now.month, year=now.year, hour=now.hour,
                                    minute=now.minute, second=1)
            if now > old:
                ddate = round((now - old).seconds.numerator / 60)
            else:
                ddate = round((old - now).seconds.numerator / 60)
            return ddate
        return "ثبت نشده"

    def nowdate(self):
        if self.updatedate:
            jd = JDate(self.updatedate.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('Y/m/d H:i')
            return newsdate
        else:
            return 'No Result'

    def rpmdate(self):
        dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}
        dt = self.rpm_version_date.split(" ")
        if len(self.rpm_version_date) > 5:
            try:
                a = dict.get(dt[2])
                datein = datetime.date(day=int(dt[1]), month=int(a), year=int(dt[3]))
                jd = JDate(datein.strftime("%Y-%m-%d"))
                newsdate = jd.format('Y/m/d')
                return newsdate + " (" + str(dt[4]) + ")"
            except:
                return self.rpm_version_date
        return "ثبت نشده"

    def lastdate(self):
        dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}
        last_connection = self.last_connection
        if len(last_connection) > 5:
            dt = last_connection.split(" ")
            try:
                if len(dt[2]) < 1:
                    dt2 = last_connection.split("  ")
                    day = dt2[1][:1]
                    dt2 = last_connection.split(" ")
                    a = dict.get(dt2[1])
                    year = dt[6][:4]
                    time = dt[4]

                else:
                    try:
                        day = dt[2]
                        a = dict.get(dt[1])
                        year = dt[5][:4]
                        time = dt[3]
                    except:
                        day = 0
                        year = 0
                        a = 0
                        time = 0
            except:
                return last_connection
            if len(last_connection) > 5:
                try:
                    datein = datetime.date(day=int(day), month=int(a), year=int(year))
                    jd = JDate(datein.strftime("%Y-%m-%d"))
                    newsdate = jd.format('Y/m/d')
                    return newsdate + " (" + str(time) + ")"
                except:
                    return last_connection
            return "ثبت نشده"
        return "ثبت نشده"


class IpcLogHistory(models.Model):
    gs = models.ForeignKey(GsModel, null=True, blank=True, on_delete=models.CASCADE)
    gsid = models.CharField(max_length=150, blank=True)
    dore = models.PositiveIntegerField(db_index=True, blank=True)
    date_ipc = models.CharField(max_length=10, blank=True)
    time_ipc = models.CharField(max_length=10, blank=True)
    dashboard_version = models.CharField(max_length=20, blank=True)
    rpm_version = models.CharField(max_length=150, blank=True)
    rpm_version_date = models.CharField(max_length=200, blank=True)
    pt_version = models.CharField(max_length=150, blank=True)
    quta_table_version = models.CharField(max_length=150, blank=True)
    zone_table_version = models.CharField(max_length=150, blank=True)
    price_table_version = models.CharField(max_length=150, blank=True)
    blacklist_version = models.CharField(max_length=150, blank=True)
    last_connection = models.CharField(max_length=150, blank=True)
    blacklist_count = models.CharField(max_length=150, blank=True)
    hd_serial = models.CharField(max_length=170, blank=True)
    os_version = models.CharField(max_length=150, blank=True)
    bl_ipc = models.CharField(max_length=150, null=True, blank=True)
    modemname = models.CharField(max_length=10, blank=True, null=True)
    sam = models.BooleanField(default=False)
    modem = models.BooleanField(default=False)
    poler = models.BooleanField(default=False)
    datacenter = models.BooleanField(default=False)
    fasb = models.BooleanField(default=False)
    asmelat = models.BooleanField(default=False)
    mellatmodem = models.BooleanField(default=False)
    internet = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    uniq = models.CharField(max_length=20, unique=True, blank=True)
    contradiction = models.BooleanField(default=False)
    updatedate = models.DateTimeField(null=True, blank=True)
    ck_rpm_version = models.BooleanField(default=True)
    ck_dashboard_version = models.BooleanField(default=True)
    ck_pt_version = models.BooleanField(default=True)
    ck_pt_online = models.BooleanField(default=True)
    ck_quta_table_version = models.BooleanField(default=True)
    ck_price_table_version = models.BooleanField(default=True)
    ck_zone_table_version = models.BooleanField(default=True)
    ck_blacklist_version = models.BooleanField(default=True)
    ck_blacklist_count = models.BooleanField(default=True)
    imagever = models.CharField(max_length=10, default='0', blank=True)
    gs_version = models.CharField(max_length=10, default='0', blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.gs.name

    def gsid_decode(self):

        result = decrypt(self.gsid)
        return result

    def rpm_decode(self):
        result = decrypt(self.rpm_version)

        return result

    def pt_decode(self):
        result = decrypt(self.pt_version)
        return result

    def quta_table_version_decode(self):
        result = decrypt(self.quta_table_version)

        return result

    def price_table_version_decode(self):
        result = decrypt(self.price_table_version)

        return result

    def blacklist_version_decode(self):
        result = decrypt(self.blacklist_version)

        return result

    def blacklist_count_decode(self):
        result = decrypt(self.blacklist_count)

        return result

    def zone_table_version_decode(self):
        result = decrypt(self.zone_table_version)

        return result

    def last_connection_decode(self):
        return decrypt(self.last_connection)

    def os_version_decode(self):
        return decrypt(self.os_version)

    def bl_ipc_decode(self):
        return decrypt(self.bl_ipc)

    def ipcdate(self):
        dt = self.date_ipc.split("-")
        if len(self.date_ipc) > 5:
            datein = datetime.date(day=int(dt[2]), month=int(dt[1]), year=int(dt[0]))
            jd = JDate(datein.strftime("%Y-%m-%d"))
            try:
                newsdate = jd.format('Y/m/d')
            except:
                return 'غیر قابل خوانش'
            return newsdate
        return "ثبت نشده"

    def diffdate(self):
        now = self.updatedate
        if len(self.date_ipc) > 5:
            dt = self.date_ipc.split("-")
            st = self.time_ipc.split(":")
            old = datetime.datetime(day=int(dt[2]), month=int(dt[1]), year=int(dt[0]), hour=int(st[0]),
                                    minute=int(st[1]), second=1)
            now = datetime.datetime(day=now.day, month=now.month, year=now.year, hour=now.hour,
                                    minute=now.minute, second=1)
            ddate = round((now - old).seconds.numerator / 60)
            return ddate
        return "ثبت نشده"

    def nowdate(self):
        if self.updatedate:
            jd = JDate(self.updatedate.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('Y/m/d H:i')
            return newsdate
        else:
            return 'No Result'

    def rpmdate(self):
        dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}
        dt = self.rpm_version_date.split(" ")
        if len(self.rpm_version_date) > 5:
            try:
                a = dict.get(dt[2])
                datein = datetime.date(day=int(dt[1]), month=int(a), year=int(dt[3]))
                jd = JDate(datein.strftime("%Y-%m-%d"))
                newsdate = jd.format('Y/m/d')
                return newsdate + " (" + str(dt[4]) + ")"
            except:
                return self.rpm_version_date
        return "ثبت نشده"

    def lastdate(self):
        dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}
        last_connection = self.last_connection_decode()
        if len(last_connection) > 5:
            dt = last_connection.split(" ")
            if len(dt[2]) < 1:
                dt2 = last_connection.split("  ")
                day = dt2[1][:1]
                dt2 = last_connection.split(" ")
                a = dict.get(dt2[1])
                year = dt[6][:4]
                time = dt[4]
            else:
                try:
                    day = dt[2]
                    a = dict.get(dt[1])
                    year = dt[5][:4]
                    time = dt[3]
                except:
                    day = 0
                    year = 0
                    a = 0
                    time = 0
            if len(last_connection) > 5:
                try:
                    datein = datetime.date(day=int(day), month=int(a), year=int(year))
                    jd = JDate(datein.strftime("%Y-%m-%d"))
                    newsdate = jd.format('Y/m/d')
                    return newsdate + " (" + str(time) + ")"
                except:
                    return last_connection
            return "ثبت نشده"
        return "ثبت نشده"


class PtSerial(models.Model):
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    master_serial = models.CharField(max_length=30, blank=True)
    pinpad_serial = models.CharField(max_length=30, blank=True)
    sam_serial = models.CharField(max_length=30, blank=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    dore = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.master_serial


class SellGs(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    tarikh = jmodels.jDateField(db_index=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    sell = models.PositiveIntegerField(default=0)
    yarane = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nimeyarane = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    azad1 = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    azad2 = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    azad = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ezterari = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    haveleh = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    azmayesh = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sumsell = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, db_index=True)

    object_role = RoleeManager()
    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['tarikh', 'product']),
            models.Index(fields=['gs', 'tarikh']),
        ]

    def __str__(self):
        return self.gs.gsid

    def sumsell(self):
        return self.yarane + self.azad + self.ezterari + self.azmayesh

    @classmethod
    def sell_get_or_create(cls, gs, tarikh):
        if not cls.objects.filter(gs_id=gs, tarikh=tarikh, product_id=2).exists():
            cls.objects.create(gs_id=gs, tarikh=tarikh, product_id=2)
        if not cls.objects.filter(gs_id=gs, tarikh=tarikh, product_id=3).exists():
            cls.objects.create(gs_id=gs, tarikh=tarikh, product_id=3)
        if not cls.objects.filter(gs_id=gs, tarikh=tarikh, product_id=4).exists():
            cls.objects.create(gs_id=gs, tarikh=tarikh, product_id=4)

        for item in [2, 3, 4]:
            try:
                forosh = 0
                clssell = cls.objects.get(gs_id=gs, tarikh=tarikh, product_id=item)
                sumsell = SellModel.objects.filter(gs_id=gs, tarikh=tarikh, product_id=item).aggregate(
                    sell=Sum('sell'), yarane=Sum('yarane'),nimeyarane=Sum('nimeyarane'),azad1=Sum('azad1'),azad2=Sum('azad2'),
                    azad=Sum('azad'), ezterari=Sum('ezterari'),
                    haveleh=Sum('haveleh'),
                    azmayesh=Sum('azmayesh'))

                if sumsell['sell']:
                    forosh = sumsell['sell']
                if not sumsell['sell'] and sumsell['yarane']:
                    forosh = 0
                azad = sumsell['azad'] if sumsell['azad'] else 0
                azad1 = sumsell['azad1'] if sumsell['azad1'] else 0
                azad2 = sumsell['azad2'] if sumsell['azad2'] else 0
                ezterari = sumsell['ezterari'] if sumsell['ezterari'] else 0
                haveleh = sumsell['haveleh'] if sumsell['haveleh'] else 0
                azmayesh = sumsell['azmayesh'] if sumsell['azmayesh'] else 0
                _yaraneh = sumsell['yarane'] if sumsell['yarane'] else 0
                _nimeyarane = sumsell['nimeyarane'] if sumsell['nimeyarane'] else 0
                if sumsell and azad + ezterari + azmayesh + _yaraneh > 0:
                    clssell.product_id = item
                    clssell.sell = forosh
                    clssell.yarane = sumsell['yarane']
                    clssell.azad = azad
                    clssell.nimeyarane = _nimeyarane
                    clssell.azad1 = azad1
                    clssell.azad2 = azad2
                    clssell.ezterari = ezterari
                    clssell.haveleh = haveleh
                    clssell.azmayesh = azmayesh
                    clssell.save()
                else:
                    clssell.product_id = item
                    clssell.sell = 0
                    clssell.yarane = 0
                    clssell.nimeyarane = _nimeyarane
                    clssell.azad1 = azad1
                    clssell.azad2 = azad2
                    clssell.azad = 0
                    clssell.ezterari = 0
                    clssell.haveleh = 0
                    clssell.azmayesh = 0
                    clssell.save()

            except cls.DoesNotExist:
                return False
            except MultipleObjectsReturned as e:
                doble = cls.objects.filter(gs_id=gs, tarikh=tarikh, product_id=item).first()
                doble.delete()

        # return True


class AccessChangeSell(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tarikh = jmodels.jDateField()
    editor = models.ForeignKey(Owner, on_delete=models.CASCADE)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE, blank=True, null=True)
    shname = models.CharField(max_length=60, blank=True, null=True)
    created = jmodels.jDateField(auto_now_add=True)
    updated = jmodels.jDateField(auto_now=True)
    active = models.BooleanField(default=True)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.gs.name)


class InfoEkhtelafLogs(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    pomp = models.ForeignKey(Pump, on_delete=models.CASCADE)
    status = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    tarikh = jmodels.jDateField()
    created = jmodels.jDateField(auto_now_add=True)
    updated = jmodels.jDateField(auto_now=True)
    sell = models.ForeignKey(SellModel, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.pomp.gs.name)


class CarStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CarInfo(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    tarikh = jmodels.jDateField(db_index=True)
    carstatus = models.ForeignKey(CarStatus, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return str(self.gs)


class EditSell(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    tarikh = jmodels.jDateField(auto_now_add=True)
    sell = models.ForeignKey(SellModel, on_delete=models.CASCADE)
    old = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    new = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    status = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return str(self.sell)


class AcceptForBuy(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    tarikh = jmodels.jDateField()
    ispay = models.BooleanField(default=False)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.gs)


class OtherError(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.gs.name


class Oildepot(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    created = models.DateField(auto_now_add=True)
    dalytime = models.PositiveIntegerField(default=15)

    def __str__(self):
        return self.name


class ParametrGs(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    oildepot = models.ForeignKey(Oildepot, on_delete=models.CASCADE)
    distance = models.PositiveIntegerField()
    normaltime = models.PositiveIntegerField()
    traffictime = models.PositiveIntegerField()
    normalsellinhour = models.PositiveIntegerField(default=0)
    trafficsellinhour = models.PositiveIntegerField(default=0)
    normalsellinhoursuper = models.PositiveIntegerField(default=0)
    normalsellinhourgaz = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.gs.name


class SellGsInHour(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    h1time = models.PositiveIntegerField()
    h2time = models.PositiveIntegerField()
    h3time = models.PositiveIntegerField()
    h4time = models.PositiveIntegerField()
    h5time = models.PositiveIntegerField()
    h6time = models.PositiveIntegerField()
    h7time = models.PositiveIntegerField()
    h8time = models.PositiveIntegerField()
    h9time = models.PositiveIntegerField()
    h10time = models.PositiveIntegerField()
    h11time = models.PositiveIntegerField()
    h12time = models.PositiveIntegerField()
    h13time = models.PositiveIntegerField()
    h14time = models.PositiveIntegerField()
    h15time = models.PositiveIntegerField()
    h16time = models.PositiveIntegerField()
    h17time = models.PositiveIntegerField()
    h18time = models.PositiveIntegerField()
    h19time = models.PositiveIntegerField()
    h20time = models.PositiveIntegerField()
    h21time = models.PositiveIntegerField()
    h22time = models.PositiveIntegerField()
    h23time = models.PositiveIntegerField()
    h24time = models.PositiveIntegerField()

    def __str__(self):
        return str(self.gs)


class OpenCloseSell(models.Model):
    choice = {
        ('open', 'باز کردن فروش'),
        ('close', 'بستن فروش'),
    }
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name="نام کاربر")
    tarikh = models.CharField('تاریخ فروش', max_length=11)
    status = models.CharField('عملیات', max_length=5, choices=choice)
    created_at = models.DateTimeField(auto_now_add=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name='نام جایگاه')
    dore = jmodels.jDateField(null=True, blank=True)

    def __str__(self):
        return str(self.gs)

    @classmethod
    def create_log(cls, owner, tarikh, gs, status):
        tarikh2 = tarikh.split("-")
        tarikh2 = jdatetime.date(day=int(tarikh2[2]), month=int(tarikh2[1]), year=int(tarikh2[0])).togregorian()
        return cls.objects.create(owner_id=owner, tarikh=tarikh, gs_id=gs, status=status, dore=tarikh2)


class CloseSellReport(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name="کاربر", blank=True, null=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tarikh = jmodels.jDateField(db_index=True)
    status = models.PositiveIntegerField()

    def __str__(self):
        return str(self.gs)


class ModemDisconnect(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name='نام جایگاه')
    tarikh = models.DateField(db_index=True)
    starttime = models.CharField(max_length=20, blank=True, null=True)
    endtime = models.CharField(max_length=20, blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.gs.gsid)


class ReceivedBarname(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    tarikh = models.DateField()
    barname_number = models.CharField(max_length=50)
    receive_date = models.DateField()
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['gs', 'tarikh', 'barname_number']


class ProductId(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='نوع فرآورده')
    productid = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "شناسه فرآورده"
        verbose_name_plural = "شناسه های فرآورده"

    def __str__(self):
        return f"{self.product} - {self.productid} - {self.name}"


class SendType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Sender(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="کد فرستنده")
    name = models.CharField(max_length=100, verbose_name="نام فرستنده")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="مختصات جغرافیایی")

    class Meta:
        verbose_name = "فرستنده"
        verbose_name_plural = "فرستندگان"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Waybill(models.Model):
    gsid = models.ForeignKey(GsModel, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    waybill_id = models.CharField(

        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="شماره بارنامه"
    )
    product_id = models.ForeignKey(
        ProductId, on_delete=models.CASCADE,
        max_length=50,
        db_index=True,
        verbose_name="شناسه فرآورده"
    )
    quantity = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="میزان فرآورده"
    )
    quantity60 = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="میزان فرآورده در 60 درجه"
    )
    weight = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="وزن"
    )
    degree = models.FloatField(
        verbose_name="درجه حرارت"
    )
    special_weight = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="وزن مخصوص"
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name="نام مشتری"
    )
    exit_date = models.DateField(
        db_index=True,
        verbose_name="تاریخ خروج"
    )
    exit_time = models.TimeField(
        verbose_name="زمان خروج"
    )
    full_plak_with_seri = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="شماره پلاک"
    )
    contract_code_car = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="کد پیمانکار"
    )
    car_driving_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نام راننده"
    )
    car_driving_mobail = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="موبایل راننده"
    )
    customer_code = models.CharField(
        max_length=50,
        verbose_name="کد مشتری"
    )
    received_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
        verbose_name="زمان دریافت داده"
    )

    received_quantity = models.FloatField(
        blank=True, null=True,
        verbose_name="مقدار رسید"
    )

    send_type = models.ForeignKey(
        SendType,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="وضعیت ارسال"
    )
    sender = models.PositiveIntegerField(blank=True, null=True, )
    sender_new = models.ForeignKey(
        Sender,
        db_index=True,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        to_field="code",
        verbose_name="فرستنده"
    )
    target = models.PositiveIntegerField(blank=True, null=True, )
    receive_date = models.DateField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name="تاریخ رسید"
    )
    receive_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="زمان رسید"
    )

    receive_car_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ رسیدن نفتکش"
    )

    receive_car_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="زمان رسیدن نفتکش"
    )

    class Meta:
        verbose_name = "بارنامه"
        verbose_name_plural = "بارنامه‌ها"

    def __str__(self):
        return f"{self.waybill_id} - {self.customer_name}"


@receiver(pre_save, sender=Waybill)
def calculate_receive_car_datetime(sender, instance, **kwargs):
    if instance.sender and not instance.sender_new:
        try:
            instance.sender_new_id = instance.sender
        except Sender.DoesNotExist:
            pass
    if instance.exit_date and instance.exit_time and instance.gsid:
        try:
            # دریافت مدت زمان سفر از مدل ParametrGs
            parametr_gs = ParametrGs.objects.get(gs=instance.gsid)
            travel_minutes = parametr_gs.normaltime

            # ایجاد آبجکت datetime از تاریخ و زمان خروج
            exit_datetime = datetime.datetime.combine(instance.exit_date, instance.exit_time)

            # اضافه کردن مدت زمان سفر
            receive_datetime = exit_datetime + timedelta(minutes=travel_minutes)

            # ذخیره در فیلدهای مربوطه
            instance.receive_car_date = receive_datetime.date()
            instance.receive_car_time = receive_datetime.time()

        except ParametrGs.DoesNotExist:
            # اگر ParametrGs برای این جایگاه وجود نداشته باشد
            pass
        except Exception as e:
            print(f" {e}")


class DiscrepancyApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('pendingarea', 'تایید ناحیه > منتظر تایید مهندسی'),
        ('engineering_approved', 'تایید مهندسی > منتظر تایید رئیس سامانه'),
        ('system_approved', 'تایید سامانه > تکمیل شد'),
        ('rejected', 'رد شده'),
    ]

    sell = models.ForeignKey(SellModel, on_delete=models.CASCADE, related_name='discrepancies')
    area_head = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='area_discrepancies')
    discrepancy_amount = models.DecimalField(max_digits=20, decimal_places=2)
    discrepancy_date = jmodels.jDateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    engineering_approver = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='engineering_approvals')
    system_approver = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='system_approvals')

    class Meta:
        verbose_name = 'تاییدیه مغایرت'
        verbose_name_plural = 'تاییدیه مغایرت‌ها'
        ordering = ['-discrepancy_date']

    def __str__(self):
        return f"{self.sell.gs.name} - {self.discrepancy_amount}"


@receiver(post_save, sender=SellModel)
def check_discrepancy(sender, instance, created, **kwargs):
    try:
        if int(instance.nomojaz) <= 50:
            DiscrepancyApproval.objects.filter(sell=instance).delete()
        if int(instance.nomojaz) > 50:  # اگر مغایرت غیرمجاز بیش از 50 لیتر باشد
            # بررسی آیا 20 روز از تاریخ فروش گذشته است
            discrepancy_date = instance.tarikh
            # پیدا کردن رئیس ناحیه مربوطه
            area_head = Owner.objects.filter(
                role__role='area',
                refrence_id=3,
                area=instance.gs.area
            ).first()

            if area_head:

                # ایجاد درخواست تایید
                try:
                    _dis = DiscrepancyApproval.objects.get(sell=instance)
                    _dis.discrepancy_amount = instance.nomojaz
                    _dis.save()

                except DiscrepancyApproval.DoesNotExist:
                    DiscrepancyApproval.objects.get_or_create(
                        sell=instance,
                        area_head=area_head,
                        discrepancy_amount=instance.nomojaz,
                        discrepancy_date=discrepancy_date
                    )
    except:
        pass


# class ErroreWabillApi(models.Model):
#     info = models.TextField()
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.info

class ConsumptionPolicy(models.Model):
    POLICY_TYPES = [
        ('regional_quota', 'سهمیه‌بندی منطقه‌ای'),
        ('emergency', 'شرایط اضطراری'),
        ('card_type_limit', 'محدودیت نوع کارت'),
        ('time_based', 'محدودیت زمانی'),
    ]

    CARD_TYPES = [
        ('personal', 'شخصی'),
        ('governmental', 'دولتی'),
        ('public', 'عمومی'),
        ('all', 'همه'),
    ]

    name = models.CharField(max_length=200, verbose_name="نام سیاست")
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES, verbose_name="نوع سیاست")
    description = models.TextField(verbose_name="توضیحات", blank=True)

    # محدوده زمانی سیاست
    start_date = jmodels.jDateField(verbose_name="تاریخ شروع")
    end_date = jmodels.jDateField(verbose_name="تاریخ پایان", null=True, blank=True)

    # مناطق تحت تأثیر
    zones = models.ManyToManyField(Zone, verbose_name="مناطق تحت تأثیر", blank=True)

    # محصولات تحت تأثیر
    products = models.ManyToManyField(Product, verbose_name="فرآورده‌های تحت تأثیر")

    # محدودیت‌ها
    daily_limit = models.PositiveIntegerField(verbose_name="محدودیت روزانه (لیتر)", default=0)
    transaction_limit = models.PositiveIntegerField(verbose_name="محدودیت هر تراکنش (لیتر)", default=0)

    # نوع کارت‌های مستثنی
    excluded_card_types = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        default='all',
        verbose_name="کارت‌های مستثنی"
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سیاست مصرف"
        verbose_name_plural = "سیاست‌های مصرف"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_currently_active(self):
        """آیا سیاست در حال حاضر فعال است؟"""
        today = jdatetime.date.today()
        if self.end_date:
            return self.start_date <= today <= self.end_date and self.is_active
        return self.start_date <= today and self.is_active


class QRScan(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name='کد جایگاه')
    qr_data1 = models.TextField(verbose_name='داده رمزینه')
    qr_data2 = models.TextField(verbose_name='داده رمزینه')
    dore = models.CharField(verbose_name='تاریخ دوره', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'اسکن رمزینه'
        verbose_name_plural = 'اسکن‌های رمزینه'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.gs} - {self.dore}"

    def save(self, *args, **kwargs):
        # ذخیره رکورد جدید
        super().save(*args, **kwargs)

        # حذف رکوردهای قدیمی‌تر از ۱۰ مورد برای این جایگاه و تاریخ
        self.cleanup_old_records()

    def cleanup_old_records(self):
        """حذف رکوردهای قدیمی‌تر از ۱۰ مورد برای هر جایگاه در هر تاریخ"""
        # پیدا کردن تمام رکوردهای این جایگاه در این تاریخ
        same_day_records = QRScan.objects.filter(
            gs=self.gs,
        ).order_by('-created_at')

        # اگر بیش از ۱۰ رکورد وجود دارد، قدیمی‌ترها را حذف کن
        if same_day_records.count() > 10:
            records_to_delete = same_day_records[10:]
            for record in records_to_delete:
                record.delete()


class SellTime(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    datein = models.CharField(max_length=25)
    dateout = models.CharField(max_length=25)
    status = models.BooleanField(default=False)
    date_in_jalali = jmodels.jDateTimeField(null=True, blank=True)
    date_out_jalali = jmodels.jDateTimeField(null=True, blank=True)

    def __str__(self):
        return self.gs.name


class QrTime(models.Model):
    selltime = models.ForeignKey(SellTime, on_delete=models.CASCADE, db_index=True)
    tolombeinfo = models.ForeignKey(Pump, on_delete=models.CASCADE, db_index=True)
    pumpnumber = models.PositiveIntegerField(blank=True)
    yarane = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    nimeyarane = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azad1 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azad = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    ezterari = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    haveleh = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    azmayesh = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.selltime
