import os
import random
import uuid
from django.db.models.functions import ExtractHour, TruncDate, ExtractWeek, ExtractYear
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django_jalali.db import models as jmodels
from django.utils import timezone
import math
from django.db.models.signals import post_save, post_delete
from jalali.Jalalian import JDate
from django.db import IntegrityError
from django.conf import settings
import re
from .modelmanager import RoleeManager
from django.db.models import Count, Sum, Q, Avg, Case, When, F
from datetime import date, timedelta
import datetime
import socket


class IsZoneManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(iszone=True)


class Zone(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    tekcount = models.PositiveIntegerField(blank=True)
    storage = models.BooleanField(default=False)
    iszone = models.BooleanField(default=True)
    setinday = models.PositiveIntegerField(default=30)
    setamount = models.PositiveIntegerField(default=1)
    setsellday = models.PositiveIntegerField(default=4)
    setrejectticket = models.PositiveIntegerField(default=0)
    iscoding = models.BooleanField(default=False)
    ticket_benzin = models.BooleanField(default=True)
    ticket_super = models.BooleanField(default=True)
    ticket_gaz = models.BooleanField(default=True)
    bypass_sell = models.BooleanField(default=False)
    issejelli = models.BooleanField(default=False)
    showdashboard = models.BooleanField(default=False)
    iscloseticketissell = models.BooleanField(default=True, verbose_name="بستن سیستمی تیکت دارای فروش")
    zoneid = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    objects = models.Manager()
    objects_all = models.Manager()
    objects_limit = IsZoneManager()

    class Admin:
        manager = models.Manager()


class Area(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='relzone')
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    long = models.CharField(max_length=10, blank=True, null=True)
    areaid = models.CharField(max_length=4, blank=True, null=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=5, blank=True)
    showlevel = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class Refrence(models.Model):
    name = models.CharField(max_length=100)
    showlevel = models.PositiveIntegerField(default=1)
    ename = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Storage(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True, related_name='storagetozone')
    level = models.PositiveIntegerField(blank=True, null=True)
    iszarib = models.BooleanField(default=False)
    zarib = models.PositiveIntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    sortid = models.PositiveIntegerField(default=20)
    refrence = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Education(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def convert_persian_to_english_digits(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian_digit, english_digit in persian_to_english.items():
        text = text.replace(persian_digit, english_digit)
    return text


def validate_serial_number(value):
    # تبدیل اعداد فارسی به انگلیسی
    cleaned_value = convert_persian_to_english_digits(value)
    # حذف خط فاصله و اسپیس
    cleaned_value = re.sub(r'[- ]', '', cleaned_value)
    # بررسی اینکه فقط شامل اعداد انگلیسی باشد
    if not re.match(r'^[0-9]+$', cleaned_value):
        raise ValidationError('کد ملی فقط باید شامل اعداد انگلیسی باشد و نباید حاوی خط فاصله یا اسپیس باشد.')
    return cleaned_value  # برای ذخیره‌سازی مقدار اصلاح‌شده


class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    national_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Owner(models.Model):
    choice = {
        ('marid', 'متاهل'),
        ('singel', 'مجرد'),
    }
    choice2 = {
        ('1', 'آقا'),
        ('2', 'خانم'),
    }
    choice3 = {
        ('1', 'پایان خدمت'),
        ('2', 'معاف'),
        ('3', 'هیچکدام'),
    }

    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"

        filename = f"{unique_id}.{ext}"
        return os.path.join("img/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 300
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 300
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=100)
    lname = models.CharField(max_length=100, blank=True)
    mobail = models.CharField(max_length=14)
    codemeli = models.CharField(max_length=14, unique=True, db_index=True, validators=[validate_serial_number])
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    create = models.DateTimeField(auto_now_add=True, blank=True)
    active = models.BooleanField(default=True)
    img = models.ImageField(upload_to=wrapper, blank=True, validators=[validate_image])
    refrence = models.ForeignKey(Refrence, on_delete=models.CASCADE, null=True, blank=True)
    colorpage = models.PositiveIntegerField(blank=True, default=1)
    isboarder = models.BooleanField(default=False)
    viewtickets = models.PositiveIntegerField(blank=True, default=1)
    childcount = models.PositiveIntegerField(blank=True, default=0)
    shomare = models.BooleanField(blank=True, default=True)
    sarfasl = models.BooleanField(blank=True, default=True)
    onvan = models.BooleanField(blank=True, default=True)
    zoner = models.BooleanField(blank=True, default=True)
    arear = models.BooleanField(blank=True, default=True)
    gsid = models.BooleanField(blank=True, default=True)
    gsname = models.BooleanField(blank=True, default=True)
    nazel = models.BooleanField(blank=True, default=True)
    product = models.BooleanField(blank=True, default=True)
    createtime = models.BooleanField(blank=True, default=True)
    creator = models.BooleanField(blank=True, default=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    daghimande = models.BooleanField(default=False)
    education = models.ForeignKey(Education, on_delete=models.CASCADE, null=True, blank=True)
    place_of_birth = models.CharField(max_length=100, blank=True)
    date_of_birth = models.CharField(max_length=10, blank=True)
    marital_status = models.CharField(max_length=10, choices=choice, null=True, blank=True)
    start_date = models.CharField(max_length=10, blank=True)
    job_group = models.PositiveIntegerField(blank=True, default=7)
    accountnumber = models.CharField(max_length=30, null=True, blank=True)
    shsh = models.CharField(max_length=11, null=True, blank=True)
    sodor = models.CharField(max_length=31, null=True, blank=True)
    father = models.CharField(max_length=31, null=True, blank=True)
    mysex = models.CharField(max_length=1, choices=choice2, null=True, blank=True)
    khedmat = models.CharField(max_length=1, choices=choice3, null=True, blank=True)
    api_key = models.CharField(max_length=100, blank=True)
    qrcode = models.TextField(blank=True)
    qrcode2 = models.TextField(blank=True)
    mobail_ischeck = models.BooleanField(default=False)
    defaultstorage = models.PositiveIntegerField(default=1)
    locked = models.BooleanField(default=False)
    lockedsendsms = models.BooleanField(default=False)
    numbersms = models.IntegerField(default=0)
    numberfaildpassword = models.IntegerField(default=0)
    datelocked = models.DateTimeField(blank=True, null=True)
    endsendsms = models.DateTimeField(blank=True, null=True)
    oildepot = models.ForeignKey("sell.Oildepot", on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return "%s %s" % (self.name, self.lname)

    def calculate_child_count(self):
        # تعداد فرزندهای فعال و دارای مدارک (تصویر)
        count = OwnerChild.objects.filter(
            owner=self,
            img__isnull=False  # بررسی وجود تصویر (مدارک)
        ).count()

        return count

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.name, self.lname)
        return full_name.strip()

    @classmethod
    def commit_qrcode(cls, qrcodes: str, id: int):
        owner = Owner.objects.get(id=id)
        if owner.qrcode == None:
            owner.qrcode = ""
        if qrcodes in owner.qrcode:
            owner.qrcode = ""
        owner.qrcode = str(owner.qrcode) + str(qrcodes)
        owner.save()

    @classmethod
    def del_qrcode(cls, id: int):
        owner = Owner.objects.get(id=id)
        owner.qrcode = ""
        owner.save()
        return True

    def pdate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d')
        return newsdate


class City(models.Model):
    name = models.CharField(max_length=50)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class PermissionService:
    @staticmethod
    def create_default_permissions(permission):
        for role in Role.objects.all():
            for ref in Refrence.objects.all():
                try:
                    uniq = f"{ref.id}-{role.id}-{permission.id}"
                    if not DefaultPermission.objects.filter(unid=uniq).exists():
                        DefaultPermission.objects.create(
                            role_id=role.id,
                            semat_id=ref.id,
                            accessrole_id=5,
                            permission_id=permission.id,
                            unid=uniq
                        )
                except IntegrityError:
                    continue

    @staticmethod
    def create_user_permissions(permission):
        for owner_id in UserPermission.objects.values_list('owner_id', flat=True).distinct():
            try:
                uniq = f"{owner_id}-{permission.id}"
                if not UserPermission.objects.filter(unid=uniq).exists():
                    UserPermission.objects.create(
                        accessrole_id=5,
                        permission_id=permission.id,
                        unid=uniq,
                        owner_id=owner_id
                    )
            except IntegrityError:
                continue


class Permission(models.Model):
    info = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    isrole = models.BooleanField(default=False)
    Sortper = models.ForeignKey('Permission', null=True, blank=True, on_delete=models.CASCADE)
    permit = models.IntegerField(default=0)
    cat_sort = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.info


def defultpermission_post_save(sender, instance, created, *args, **kwargs):
    if created:
        PermissionService.create_default_permissions(instance)
        PermissionService.create_user_permissions(instance)


post_save.connect(defultpermission_post_save, sender=Permission)


class StatusMoavagh(models.Model):
    name = models.CharField(max_length=400)
    info = models.CharField(max_length=405)
    ename = models.CharField(max_length=15, blank=True)
    issla = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AccessRole(models.Model):
    name = models.CharField(max_length=15)
    ename = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name


class AccessList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    accesslist = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(AccessRole, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.first_name


class DefaultPermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    semat = models.ForeignKey(Refrence, on_delete=models.CASCADE, null=True, blank=True)
    accessrole = models.ForeignKey(AccessRole, on_delete=models.CASCADE, null=True, blank=True)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    unid = models.CharField(max_length=10, unique=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True)
    ischange = models.BooleanField(default=False)

    def __str__(self):
        return self.role.name


def defultpermissionupdate_post_save(sender, instance, created, *args, **kwargs):
    data = instance

    queryset = UserPermission.objects.values('owner_id').filter(owner__role_id=data.role_id,
                                                                owner__refrence_id=data.semat_id).annotate(a=Sum('id'))
    for item in queryset:
        try:
            if data.ischange:
                user = UserPermission.objects.get(unid=str(item['owner_id']) + "-" + str(data.permission_id))
                user.accessrole_id = data.accessrole_id
                user.save()
        except IntegrityError:
            continue
        except ObjectDoesNotExist:
            continue


post_save.connect(defultpermissionupdate_post_save, sender=DefaultPermission)


class UserPermission(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True, related_name='user_permissions')
    accessrole = models.ForeignKey(AccessRole, on_delete=models.CASCADE, null=True, blank=True)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    unid = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.owner.name + ' ' + self.owner.lname


class Operator(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست اپراتور APN '
        verbose_name = 'اپراتور'


class Rack(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست مدل رک ها '
        verbose_name = 'مدل رک'


class Modem(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست انواع مودم '
        verbose_name = 'مودم'


class Ipc(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست انواع سرور ها '
        verbose_name = 'سرور'


class GsStatus(models.Model):
    name = models.CharField(max_length=30)
    iscity = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=120)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'تعریف وضعیت جایگاه '
        verbose_name = 'وضعیت'


class Brand(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست شرکت های برند '
        verbose_name = 'برند'


class Printer(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست مدل پرینتر ها '
        verbose_name = 'مدل پرینتر'


class ThinClient(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'لیست مدل thinclients '
        verbose_name = 'مدل thinclient'


class GsModel(models.Model):

    """جدول اطلاعات جایگاه"""

    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"

        filename = f"{unique_id}.{ext}"
        return os.path.join("sejjeli/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 300
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 300
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    gsid = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=110)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, blank=True, null=False)
    simcart = models.CharField(max_length=11, blank=True, null=True, verbose_name='شماره سیم کارت مودم')
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, default=100, null=True, blank=True, verbose_name='مدل رک')
    is_montakhab = models.BooleanField(default=False, null=True, blank=True, verbose_name='منتخب نفتگاز')
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, default=100, null=True, blank=True,
                                 verbose_name='اپراتور سیم کارت')
    sejelli = models.ImageField(blank=True, upload_to=wrapper, validators=[validate_image], verbose_name='تصویر سجلی')
    sejjeli_date = jmodels.jDateField(blank=True, verbose_name='تاریخ  سجلی')
    m_benzin = models.PositiveIntegerField(blank=True, verbose_name='ظرفیت مخزن بنزین')
    m_super = models.PositiveIntegerField(blank=True, verbose_name='ظرفیت مخزن سوپر')
    m_naftgaz = models.PositiveIntegerField(blank=True, verbose_name='ظرفیت مخزن نفتگاز')
    modem = models.ForeignKey(Modem, on_delete=models.CASCADE, default=100, null=True, blank=True,
                              verbose_name='مدل مودم')
    ipc = models.ForeignKey(Ipc, on_delete=models.CASCADE, default=100, null=True, blank=True,
                            verbose_name='مدل سرور جایگاه')
    location = models.CharField(max_length=50, default='0,0', null=True, blank=True, verbose_name='مشخصات جغرافیایی')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True, verbose_name='وضعیت فعلی')
    percent = models.PositiveIntegerField(default=10, blank=True, verbose_name='')
    product = models.ManyToManyField('Product', blank=True, verbose_name='انتخاب فرآورده ها')
    nazel_kol = models.PositiveIntegerField(blank=True, verbose_name='-')
    nazel_samane = models.PositiveIntegerField(blank=True, verbose_name='-')
    nazel_teh = models.PositiveIntegerField(blank=True, verbose_name='-')
    nazel_avg = models.PositiveIntegerField(blank=True, verbose_name='-')
    initial_visit = models.BooleanField(default=False, blank=True, verbose_name='بازدید اولیه')
    koroki = models.ImageField(blank=True, upload_to=wrapper, validators=[validate_image], verbose_name='تصویر کروکی')
    req_equipment = models.CharField(max_length=50, blank=True, verbose_name='شماره نامه درخواست تجهیزات ')
    equipment_date = jmodels.jDateField(blank=True, verbose_name='تاریخ نامه درخواست تجهیزات')
    flock = models.ImageField(blank=True, upload_to="flock/", verbose_name='تصویر تست فلوک')
    flock_date = jmodels.jDateField(blank=True, verbose_name='تاریخ انجام تست فلوک')
    final_visit = models.BooleanField(default=False, blank=True, verbose_name='بازدید نهایی انجام شد؟')
    start_date = jmodels.jDateField(blank=True, verbose_name='تاریخ افتتاح')
    melat_equipment = models.CharField(max_length=50, blank=True, verbose_name='شماره نامه تجهیزات بانکی')
    melat_equipment_date = jmodels.jDateField(blank=True, verbose_name='تاریخ نامه تجهیزات بانکی')
    sam = models.CharField(max_length=50, blank=True, verbose_name='شماره نامه درخواست SAM')
    sam_date = jmodels.jDateField(blank=True, verbose_name='تاریخ نامه درخواست SAM')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='کد پستی ')
    telldaftar = models.CharField(max_length=11, blank=True, verbose_name='تلفن دفتر جایگاه')
    isqrcode = models.BooleanField(default=False, verbose_name=' ثبت اتوماتیک qrcode')
    arbain = models.BooleanField(default=False)
    isonline = models.BooleanField(default=False)
    isbank = models.BooleanField(blank=True, null=True, default=True)
    ispaystation = models.BooleanField(blank=True, null=True, default=True)
    zone_table_version = models.CharField(max_length=10, default=0, verbose_name='شماره آخرین جدول سهمیه منطقه ایی')
    iscoding = models.BooleanField(default=False, verbose_name='در طرح کدینگ')
    iszonetable = models.BooleanField(default=True, verbose_name='ثبت تیکت اتوماتیک جدول سهمیه')
    issell = models.BooleanField(default=True, verbose_name='مجوز خرید فرآورده')
    isazadforsell = models.BooleanField(default=True, verbose_name='خرید مابه التفاوت دارد')
    issab = models.BooleanField(default=False, verbose_name='جایگاه صعب العبور')
    isticket = models.BooleanField(default=True, verbose_name='مجوز ثبت تیکت')
    gsstatus = models.ForeignKey(GsStatus, on_delete=models.CASCADE, default=100, verbose_name='وضعیت مکانی جایگاه',
                                 blank=True,
                                 null=True)
    gpssignal = models.BooleanField(default=True, verbose_name='وضعیت سیگنال GPS')
    isbankmeli = models.BooleanField(default=False, verbose_name='paystation بانک ملی')
    isselldelete = models.BooleanField(default=False, verbose_name='مجوز حذف فروش')
    tedadnazelmohandesi = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد مجاز نازل معیوب مکانیکی')
    rnd = models.CharField(max_length=100, default="0")
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    btmt = models.BooleanField(default=False)
    addsell = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True, verbose_name='نام شرکت برند')
    sellcode = models.IntegerField(default=0, verbose_name='کد سامانه فروش')
    malicode = models.IntegerField(default=0, verbose_name='کد سامانه مالی')
    printer = models.ForeignKey(Printer, default=100, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='مدل پرینتر')
    thinclient = models.ForeignKey(ThinClient, default=100, on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name='مدل thinclient')

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # code = random.randint(10000000, 99999999)
        # self.rnd = code
        if self.status_id == 1:
            self.active = True
        else:
            self.active = False
        super().save(force_insert, force_update, *args, **kwargs)

    def pdate(self):
        if self.update:
            jd = JDate(self.update.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('Y/m/d H:i')
            return newsdate
        else:
            return 'No Result'

    @property
    def percent(self):
        percent1 = 0
        if self.initial_visit:
            percent1 = 10
        if self.koroki:
            percent1 = 20
        if self.req_equipment:
            percent1 = 30
        if self.sejelli:
            percent1 = 40
        if self.sam:
            percent1 = 50
        if self.flock:
            percent1 = 60
        if self.melat_equipment:
            percent1 = 70
        if self.final_visit:
            percent1 = 80
        if self.start_date:
            percent1 = 100

        return percent1

    class Meta:
        verbose_name_plural = 'لیست جایگاه ها'
        verbose_name = 'جایگاه'


class GsList(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, related_name='gsowner')

    def __str__(self):
        return self.gs.name


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PumpBrand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Statuspump(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Pump(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, related_name='gsall', verbose_name='نام جایگاه')
    number = models.PositiveIntegerField(verbose_name="شماره نازل")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='نام فرآورده')
    master = models.CharField(max_length=20, blank=True)
    pinpad = models.CharField(max_length=20, blank=True)
    pumpbrand = models.ForeignKey(PumpBrand, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    actived = models.BooleanField(default=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniq = models.CharField(max_length=10, blank=True, unique=True)
    sakoo = models.PositiveIntegerField(blank=True, verbose_name="سکو")
    nazelcountshomarande = models.PositiveIntegerField(default=0, blank=True, null=True)
    tolombe = models.PositiveIntegerField(blank=True, verbose_name="تلمبه")
    status = models.ForeignKey(Statuspump, on_delete=models.CASCADE, default=1, null=True, blank=True)
    makhzan = models.IntegerField(null=True, blank=True)
    sortnumber = models.PositiveIntegerField(default=0)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.number) + " " + str(self.product.name)

    class Meta:
        ordering = ['gs__area__zone', 'gs__area', 'gs']

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.status_id == 1:
            self.active = True

        if self.status_id in [3, 4]:
            self.actived = False
        else:
            self.actived = True
        if self.sortnumber == 0:
            self.sortnumber = self.number
        if not self.sortnumber:
            self.sortnumber = self.number

        super().save(force_insert, force_update, *args, **kwargs)


class Organization(models.Model):
    name = models.CharField(max_length=100)
    organiztion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class FailureCategory(models.Model):
    info = models.CharField(max_length=100)

    def __str__(self):
        return self.info


class FailureSub(models.Model):
    choice = {
        ('fani', 'خدمات فنی'),
        ('test', 'تست و راه اندازی'),
        ('engin', 'مهندسی'),
        ('shef', 'رئیس سامانه هوشمند'),
        ('hoze', 'رئیس حوزه'),
        ('area', 'رئیس ناحیه'),
        ('netwo', 'شبکه و زیر ساخت'),
        ('gts', 'پشتیبانی GTS'),
    }
    failurecategory = models.ForeignKey(FailureCategory, on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name="سرفصل تیکت")
    info = models.CharField(max_length=100, verbose_name="شرح")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     verbose_name='پس از ایجاد تیکت به چه کسی ارجاع گردد')
    level = models.PositiveIntegerField(
        verbose_name="چه سطحی میتواند این نوع تیکت را ایجاد کند : 1 جایگاه - 2  تکنسین -  3  منطقه")  ###Permission
    isnazel = models.BooleanField(default=False, verbose_name="برای این خرابی شماره نازل درخواست گردد")
    isclosetek = models.BooleanField(default=True, verbose_name="امکان بستن تیک توسط تکنسین وجود داشته باشد")
    organizationclose = models.CharField(max_length=7, choices=choice, blank=True,
                                         verbose_name="نام واحدی که میتواند فقط این نوع خرابی را ببندد.")
    closebyqrcode = models.BooleanField(default=False, verbose_name="رسیدگی با اسکن رمزینه")
    active = models.BooleanField(default=True, verbose_name='فعال')
    autoclosebyqrcode = models.BooleanField(default=False, verbose_name="تیکت در صورت نصب RPM  با اسکن رمزینه بسته شود")
    editable = models.BooleanField(default=True, verbose_name='شرح خرابی قابل ویرایش باشد؟')
    isscanqrcod10minago = models.BooleanField(default=False,
                                              verbose_name='برای این نوع خرابی نیاز است قبل از ایجاد تیکت ، حتما رمزینه اسکن بشود؟')
    enname = models.CharField(max_length=10, default='0')
    ischange = models.BooleanField(default=False, verbose_name='آیتم هایی که باید بعنوان تیکت مجزا ثبت شوند ')

    def __str__(self):
        return self.info


class StatusTicket(models.Model):
    info = models.CharField(max_length=100)
    status = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.info


class Reply(models.Model):
    info = models.CharField(max_length=200)
    changemaster = models.BooleanField(default=False, verbose_name='کارتخوان تعویض گردد')
    changepinpad = models.BooleanField(default=False, verbose_name='صفحه کلید تعویض گردد')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    sort_id = models.PositiveIntegerField(blank=True)
    forwarditem = models.BooleanField(blank=True, default=False)
    isdaghimaster = models.BooleanField(default=False, verbose_name='داغی کارتخوان درخواست گردد')
    isdaghipinpad = models.BooleanField(default=False, verbose_name='داغی صفحه کلید درخواست گردد')
    nocloseafteraccept = models.BooleanField(default=False, verbose_name='تیکت پس از رسیدگی باز بماند')
    ispeykarbandi = models.BooleanField(default=False, verbose_name=' کد پیکربندی ارائه گردد')
    active = models.BooleanField(default=True)
    failurecat = models.PositiveIntegerField(default=0, verbose_name='برای سرصل چه خرابی نمایش داده شود')
    openafterclose = models.BooleanField(default=False,
                                         verbose_name='این تیکت بعد از بسته شدن بتواند توسط کاربر مجدد باز شود')
    closebysmart = models.BooleanField(default=False, verbose_name='تیکت پس از رسیدگی باید توسط رئیس سامانه بسته شود')

    def __str__(self):
        return self.info


class Ticket(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, db_index=True, related_name='tickets')
    failure = models.ForeignKey(FailureSub, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    create_shamsi_year = models.CharField(max_length=4, blank=True)
    create_shamsi_month = models.CharField(max_length=2, blank=True)
    create_shamsi_day = models.CharField(max_length=2, blank=True)
    Pump = models.ForeignKey(Pump, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    descriptionowner = models.TextField(blank=True)
    actioner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    descriptionactioner = models.TextField(blank=True)
    closedate = models.DateTimeField(blank=True)
    close_shamsi_year = models.CharField(max_length=4, blank=True)
    close_shamsi_month = models.CharField(max_length=2, blank=True)
    close_shamsi_day = models.CharField(max_length=2, blank=True)
    status = models.ForeignKey(StatusTicket, on_delete=models.CASCADE)
    serialmaster = models.CharField(max_length=20, blank=True)
    serialpinpad = models.CharField(max_length=20, blank=True)
    ischange = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, default=1, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)
    statusmoavagh = models.ForeignKey(StatusMoavagh, on_delete=models.CASCADE, null=True, blank=True)
    is_system = models.BooleanField(default=False)
    star = models.PositiveIntegerField(default=0)
    shamsi_date = jmodels.jDateField(blank=True)
    close_shamsi_date = jmodels.jDateField(blank=True)
    islock = models.BooleanField(default=False)
    lockname = models.CharField(max_length=20, blank=True)
    timeaction = models.PositiveIntegerField(default=0)
    timeactionsec = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(blank=True, null=True, auto_now=True)
    foryat = models.PositiveIntegerField(default=1)
    isdaghi = models.BooleanField(default=False)
    serialdaghi = models.CharField(max_length=20, blank=True, null=True)
    rnd = models.CharField(max_length=8, default="0")
    usererja = models.PositiveIntegerField(default=0)
    temp = models.IntegerField(blank=True, null=True)
    humidity = models.IntegerField(blank=True, null=True)
    pressure = models.IntegerField(blank=True, null=True)
    main = models.CharField(max_length=50, blank=True, null=True)
    countnosell = models.PositiveIntegerField(default=0, verbose_name='تعداد روزهایی که نازل فروش نداشت')

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.gs.name

    class Meta:
        ordering = ('-id',)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.rnd == "0":
            code = random.randint(10000000, 99999999)
            self.rnd = code
        super().save(force_insert, force_update, *args, **kwargs)

    def pdate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d')
        return newsdate

    def ptime(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('H:i')
        return newsdate

    def edate(self):
        if self.closedate:
            jd = JDate(self.closedate.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('Y/m/d')
        else:
            newsdate = ''
        return newsdate

    def etime(self):
        if self.closedate:
            jd = JDate(self.closedate.strftime("%Y-%m-%d %H:%M:%S"))
            newsdate = jd.format('H:i')
        else:
            newsdate = ''

        return newsdate

    @classmethod
    def check_science(cls, gs: int, pump: int, _day: int, _amount: int):
        _today = date.today()
        try:
            si_ago_sell = _today.today() - datetime.timedelta(days=_day)
            _data = Ticket.objects.filter(gs_id=gs, Pump_id=pump, closedate__gt=si_ago_sell).aggregate(
                master=(Count(Case(When(serialmaster__gte=100, then=1)
                                   ))),
                pinpad=(Count(Case(When(serialpinpad__gte=100, then=1)
                                   ))))
            if int(_data['master']) > _amount and _amount != 0:
                TicketScience.objects.filter(gs_id=gs, status_id=1, pump_id=pump
                                             ).delete()
                TicketScience.objects.create(gs_id=gs, status_id=1, pump_id=pump,
                                             amount=int(_data['master']))
            if int(_data['pinpad']) > _amount and _amount != 0:
                TicketScience.objects.filter(gs_id=gs, status_id=2, pump_id=pump
                                             ).delete()
                TicketScience.objects.create(gs_id=gs, status_id=2, pump_id=pump,
                                             amount=int(_data['pinpad']))
        except AttributeError:
            return False
        except IntegrityError:
            return False


def ticket_post_save(sender, instance, created, *args, **kwargs):
    data = instance

    try:
        if data.Pump.id:
            if data.status_id == 1:
                pump = Pump.objects.get(id=data.Pump.id)
                pump.active = False
                pump.status_id = 2
                pump.save()
                return True
            if data.status_id == 2:
                pump = Pump.objects.get(id=data.Pump.id)
                pump.status_id = 1
                pump.active = True
                pump.save()
    except:
        return False


post_save.connect(ticket_post_save, sender=Ticket)


class StatusScience(models.Model):
    info = models.CharField(max_length=100)

    def __str__(self):
        return self.info


class TicketScience(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusScience, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    create = models.DateTimeField(auto_now_add=True)
    flag = models.BooleanField(default=False)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE, null=True, blank=True)
    information = models.CharField(max_length=100)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.gs.gsid)

    class Meta:
        unique_together = ('gs', 'status', 'pump', 'amount')


class Workflow(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    createdate = models.DateField(auto_now_add=True)
    createtime = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serialmaster = models.CharField(max_length=20, blank=True)
    serialpinpad = models.CharField(max_length=20, blank=True)
    failure = models.ForeignKey(FailureSub, on_delete=models.CASCADE, null=True, blank=True)
    lat = models.CharField(max_length=10, blank=True)
    lang = models.CharField(max_length=10, blank=True)
    serialmasterdaghi = models.CharField(max_length=20, null=True, blank=True)
    serialpinpaddaghi = models.CharField(max_length=20, null=True, blank=True)
    macaddress = models.CharField(max_length=50, null=True, blank=True, default="0")

    object_role = RoleeManager()
    objects = models.Manager()

    def __int__(self):
        return self.id

    def pdate(self):
        jd = JDate(self.createtime.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('l j E  Y')
        return newsdate

    def pdate2(self):
        jd = JDate(self.createtime.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('l  ')
        return newsdate

    def ptime(self):
        jd = JDate(self.createtime.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('H:i')
        return newsdate

    def ndate(self):
        jd = JDate(self.createtime.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d  H:i')
        return newsdate

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        try:
            hostname = socket.gethostname()
        except:
            hostname = "0"
        self.macaddress = hostname
        super().save(force_insert, force_update, *args, **kwargs)


class UploadExcel(models.Model):
    def wrapper(instance, filename, ):
        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)

        if ext not in ["xlsx", "txt", "7z"]:
            print(1)
            raise ValidationError(f"invalid image extension: {filename}")
        if ext == '7z':
            return os.path.join("post", filename)
        else:
            filename = f"{unique_id}.{ext}"
            return os.path.join("other", filename)

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 5
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    filepath = models.FileField(blank=True, upload_to=wrapper, validators=[validate_image])


class Post(models.Model):
    pan = models.CharField(max_length=100, blank=True)
    vin = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=20, blank=True)
    fuel = models.CharField(max_length=100, blank=True)
    send_date = models.CharField(max_length=15, blank=True)
    province = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.pan


class Mount(models.Model):
    mount = models.CharField(max_length=20)
    year = models.PositiveIntegerField()
    mah = models.CharField(default="01", max_length=2)
    day = models.PositiveIntegerField(default=30)
    active = models.BooleanField(default=False)
    isshow = models.BooleanField(default=True)

    # month = models.CharField(max_length=2,blank=True, null=True)

    def __str__(self):
        return str(self.year) + '-' + str(self.mount)


class Baje(models.Model):
    pan = models.CharField(max_length=20, null=True, blank=True)
    vin = models.CharField(max_length=20)
    tarikh = models.CharField(max_length=10)
    barcode = models.CharField(max_length=25)
    mobail = models.CharField(max_length=11, null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    issend = models.BooleanField(default=False)

    def __str__(self):
        return self.vin


class Parametrs(models.Model):
    dashboard_version = models.CharField(max_length=12)
    rpm_version = models.CharField(max_length=330)
    pt_version = models.CharField(max_length=10)
    quta_table_version = models.CharField(max_length=10)
    zone_table_version = models.CharField(max_length=10)
    price_table_version = models.CharField(max_length=10)
    blacklist_version = models.CharField(max_length=10)
    online_pt_version = models.PositiveIntegerField(default=0)
    bypass_sms = models.BooleanField(default=False, verbose_name="سامانه پیامک از دور خارج بشود؟")
    is_arbain = models.BooleanField(default=False, verbose_name="داشبورد اربعین ایجاد بشود؟")
    autoticketbyqrcode = models.BooleanField(default=False,
                                             verbose_name="پس از اسکن رمزینه در صورت مغایرت جدول منطقه ایی تیکت اتوماتیک صادر بشود؟")
    happyday = models.CharField(max_length=10, default=0, verbose_name="تاریخ افتتاح gts")
    isgps = models.BooleanField(default=True, verbose_name="دریافت موقعیت جغرافیایی الزامی باشد؟")
    isacceptforbuy = models.BooleanField(default=False)
    mediaurl = models.CharField(max_length=50, blank=True, null=True)
    is_saf = models.BooleanField(default=False)
    ispeykarbandi = models.BooleanField(default=True, verbose_name="کد پیکربندی ایجاد بشود؟")
    ismohasebat = models.BooleanField(default=False, verbose_name="آیتم های حقوق اتوماتیک امتیاز داده شود؟")
    func = models.BooleanField(default=True, verbose_name="تسک تعداد تیکت روزانه")
    moghayerat = models.BooleanField(default=True, verbose_name="تسک مغایرت مناطق")
    btmt = models.BooleanField(default=True, verbose_name="آیا فروش ثبت گردد؟")
    btmt2 = models.BooleanField(default=False, verbose_name="آیا آیکون پشتیبانی در داشبورد نمایش داده شود")
    msg = models.TextField(verbose_name="پیام", blank=True, null=True)
    is_event = models.BooleanField(default=True, verbose_name="آیا تاریخ و مناسبت در صفحه لاگین نمایش داده شود؟")

    def __str__(self):
        return self.dashboard_version


class CloseGS(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    date_in = models.DateField()
    date_out = models.DateField()
    status = models.PositiveIntegerField(default=1)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.gs.name)

    def datein(self):
        jd = JDate(self.date_in.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d')
        return str(newsdate)

    def dateout(self):
        jd = JDate(self.date_out.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('Y/m/d')
        return newsdate


class Scores(models.Model):
    info = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.info


class NegativeScore(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    score = models.ForeignKey(Scores, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner.name

    @classmethod
    def create_score(cls, score: int, owner: int, status: str):
        scores = Scores.objects.get(id=score)
        if scores.active:
            cls.objects.create(owner_id=owner, score_id=score, amount=scores.amount, status=status)
            return True
        else:
            return False


class WorkflowLog(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.workflow.ticket.id)

    def pdate(self):
        jd = JDate(self.created.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('l j E  Y (H:i)')
        return newsdate


class OwnerChild(models.Model):
    def wrapper(instance, filename, ):
        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"
        filename = f"{unique_id}.{ext}"
        return os.path.join("child/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 500
        if filesize > megabyte_limit * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    codemeli = models.CharField(max_length=11, unique=True)
    marid = models.CharField(max_length=1)
    bdate = jmodels.jDateField()
    sex = models.CharField(max_length=1)
    khedmat = models.CharField(max_length=1)
    img = models.ImageField(upload_to=wrapper, validators=[validate_image])
    created = models.DateTimeField(auto_now_add=True)
    imageid = models.CharField(max_length=50, default="0")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.owner.codemeli


@receiver([post_save, post_delete], sender=OwnerChild)
def update_owner_child_count(sender, instance, **kwargs):
    owner = instance.owner
    owner.childcount = owner.calculate_child_count()
    owner.save(update_fields=['childcount'])


class FilesSubject(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class OwnerFiles(models.Model):
    def wrapper(instance, filename, ):
        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"
        filename = f"{unique_id}.{ext}"
        return os.path.join("files/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 500
        if filesize > megabyte_limit * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    file = models.ForeignKey(FilesSubject, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to=wrapper, validators=[validate_image])
    uniq = models.CharField(max_length=15, unique=True)
    imageid = models.CharField(max_length=50, default="0")

    def __str__(self):
        return self.owner.codemeli


class OwnerZone(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='ownerlist')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.owner)


class AutoExcel(models.Model):
    st = models.CharField(max_length=10, blank=True, null=True)
    datein = models.CharField(max_length=20, blank=True, null=True, default=0)
    dateout = models.CharField(max_length=20, blank=True, null=True, default=0)
    titr = models.CharField(max_length=100, blank=True, null=True)
    fields = models.CharField(max_length=200, blank=True, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)
    other_id = models.PositiveIntegerField(blank=True, null=True, default=0)
    req_id = models.CharField(max_length=1000, blank=True, null=True, default=0)
    status = models.BooleanField(default=False)
    newstatus = models.BooleanField(default=False)
    errorstatus = models.BooleanField(default=False)
    reportmodel = models.PositiveIntegerField(blank=True, null=True, default=1)
    filepath = models.FileField(blank=True, upload_to="post/")
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    ended = models.DateTimeField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.owner_id)


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    role = models.ManyToManyField(Role)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    sort = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title


class TaskLogs(models.Model):
    task_id = models.CharField(max_length=5)
    info = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.task_id)


class ReInitial(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    quiz1 = models.BooleanField(default=False)
    quiz2 = models.BooleanField(default=False)
    info_quiz2 = models.DateField()
    quiz3 = models.BooleanField(default=False)
    info_quiz3 = models.CharField(max_length=200)
    quiz4 = models.BooleanField(default=False)
    quiz5 = models.BooleanField(default=False)
    ups_min = models.PositiveSmallIntegerField(default=0)
    ups_kva = models.PositiveSmallIntegerField(default=0)
    ups_battri = models.PositiveSmallIntegerField(default=0)
    ups_status_battri = models.PositiveSmallIntegerField(default=1)
    quiz6 = models.BooleanField(default=False)
    info_quiz6 = models.CharField(max_length=200)
    quiz7 = models.BooleanField(default=False)
    quiz8 = models.BooleanField(default=False)
    quiz9 = models.CharField(max_length=5)
    quiz10 = models.DateField()
    quiz11 = models.CharField(max_length=20)
    quiz12 = models.BooleanField(default=False)
    quiz13 = models.BooleanField(default=False)
    quiz14 = models.BooleanField(default=False)
    name = models.CharField(max_length=2000)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    tarikh = models.DateField(auto_now_add=True, null=True, blank=True)
    accept_gs = models.BooleanField(default=False)
    accept_tek = models.BooleanField(default=False)
    accept_zone = models.BooleanField(default=False)
    status = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.gs.gsid)

    def pdate(self):
        jd = JDate(self.create_time.strftime("%Y-%m-%d"))
        newsdate = jd.format('Y/m/d')
        return newsdate


class UploadFiles(models.Model):
    def newname(a):
        return get_random_string(length=32)

    def wrapper2(cls, filename):
        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        if ext not in ["jpg", "png", "xlsx", "pdf"]:
            raise ValidationError(f"invalid image extension: {filename}")

        filename = f"{unique_id}.{ext}"
        return os.path.join("img", filename)

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 3
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    file = models.FileField(upload_to=wrapper2, validators=[validate_image])
    fileid = models.CharField(max_length=100, default=newname("1"))
    create_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.fileid)


class DailyTicketsReport(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    st = models.SmallIntegerField(default=0)
    name = models.CharField(max_length=20, blank=True, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, blank=True, null=True)
    count_gs = models.PositiveIntegerField(default=0)
    count_pump = models.PositiveIntegerField(default=0)
    count_ticket = models.PositiveIntegerField(default=0)
    count_master = models.PositiveIntegerField(default=0)
    count_pinpad = models.PositiveIntegerField(default=0)
    master = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    pinpad = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    summ = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    created = models.DateField(auto_now_add=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.zone


class Makhzan(models.Model):
    ACTION_CHOICES = [
        ('active', 'فعال'),
        ('noactive', 'غیرفعال'),
        ('delete', 'برچیده شده'),
    ]
    create_time = models.DateTimeField(auto_now_add=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number = models.IntegerField()
    zarfyat = models.PositiveIntegerField(default=0)
    action = models.CharField(choices=ACTION_CHOICES, max_length=10, default='active')

    class Meta:
        unique_together = ('gs', 'product', 'number')

    def __str__(self):
        return self.gs.name + "-" + self.product.name

    @property
    def composite_id(self):
        return f"{self.gs_id}_{self.product_id}_{self.number}"


class NewSejelli(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    samane = models.BooleanField(default=False)
    samanename = models.CharField(max_length=20, blank=True, null=True)
    hse = models.BooleanField(default=False)
    hsename = models.CharField(max_length=20, blank=True, null=True)
    mohandesi = models.BooleanField(default=False)
    mohandesiname = models.CharField(max_length=20, blank=True, null=True)
    bazargani = models.BooleanField(default=False)
    bazarganiname = models.CharField(max_length=20, blank=True, null=True)
    nahye = models.BooleanField(default=False)
    nahyename = models.CharField(max_length=20, blank=True, null=True)
    modir = models.BooleanField(default=False)
    modirname = models.CharField(max_length=20, blank=True, null=True)
    approov = models.BooleanField(default=False)
    isok = models.BooleanField(default=False)
    okdate = models.DateTimeField(blank=True, null=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.gs.name


#
class Pump_sejjeli(models.Model):
    newsejelli = models.ForeignKey(NewSejelli, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(null=True, blank=True, verbose_name="شماره نازل")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE, verbose_name='نام فرآورده')
    pumpbrand = models.ForeignKey(PumpBrand, null=True, blank=True, on_delete=models.CASCADE)
    sakoo = models.PositiveIntegerField(null=True, blank=True, verbose_name="سکو")
    tolombe = models.PositiveIntegerField(null=True, blank=True, verbose_name="تلمبه")
    status = models.ForeignKey(Statuspump, on_delete=models.CASCADE, default=1, null=True, blank=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    makhzan = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.number) + " " + str(self.product.name)


class GsModel_sejjeli(models.Model):
    newsejelli = models.ForeignKey(NewSejelli, on_delete=models.CASCADE)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name="نام جایگاه")
    gsid = models.CharField(max_length=4, null=True, blank=True, verbose_name="شناسه جایگاه")
    name = models.CharField(null=True, blank=True, max_length=110, verbose_name="نام جایگاه")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="انتخاب ناحیه")
    telldaftar = models.CharField(max_length=15, null=True, blank=True, verbose_name="تلفن")
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")
    simcart = models.CharField(max_length=11, blank=True, verbose_name='شماره سیم کارت مودم')
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, default=100, null=True, blank=True,
                                 verbose_name='اپراتور سیم کارت')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True, verbose_name='وضعیت فعلی')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True, verbose_name='نام شرکت برند')
    sellcode = models.IntegerField(default=0, verbose_name='کد سامانه فروش')
    malicode = models.IntegerField(default=0, verbose_name='کد سامانه مالی')

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.gs.name


class Makhzan_sejjeli(models.Model):
    ACTION_CHOICES = [
        ('active', 'فعال'),
        ('noactive', 'غیرفعال'),
        ('delete', 'برچیده شده'),
    ]
    create_time = models.DateTimeField(auto_now_add=True)
    newsejelli = models.ForeignKey(NewSejelli, on_delete=models.CASCADE)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number = models.IntegerField()
    zarfyat = models.PositiveIntegerField(default=0)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='active')

    class Meta:
        unique_together = ('gs', 'product', 'number')

    def __str__(self):
        return self.gs.name + "-" + self.product.name

    @property
    def composite_id(self):
        return f"{self.gs_id}_{self.product_id}_{self.number}"


class SejelliChangeLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'ایجاد'),
        ('update', 'ویرایش'),
        ('delete', 'حذف'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sejelli = models.ForeignKey(NewSejelli, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=50)  # مانند 'Pump_sejjeli'
    record_id = models.IntegerField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changed_data = models.JSONField()  # اطلاعات تغییر کرده
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} on {self.model_name} by {self.user}"


@receiver(post_save, sender=SejelliChangeLog)
def update_newsejelli_fields(sender, instance, created, **kwargs):
    if created:
        newsejelli = instance.sejelli
        # تنظیم فیلدهای مورد نظر به False
        newsejelli.samane = False
        newsejelli.hse = False
        newsejelli.modir = False
        newsejelli.bazargani = False
        newsejelli.mohandesi = False
        newsejelli.save()


@receiver(post_save, sender=NewSejelli)
def update_approov_status(sender, instance, **kwargs):
    # بررسی آیا تمام فیلدهای مورد نظر True هستند
    required_fields = [
        instance.samane,
        instance.hse,
        instance.modir,
        instance.bazargani,
        instance.mohandesi
    ]

    # اگر همه فیلدها True باشند، approov را True کنید
    if all(required_fields):
        if not instance.approov:  # فقط در صورت تغییر ذخیره کنید
            instance.approov = True
            instance.save(update_fields=['approov'])
    else:
        if instance.approov:  # فقط در صورت تغییر ذخیره کنید
            instance.approov = False
            instance.save(update_fields=['approov'])


class TicketAnalysisManager(models.Manager):
    def _get_date_range(self, period):
        today = timezone.now().date()
        if period == 'last_week':
            start_date = today - timedelta(days=7)
        elif period == 'last_month':
            start_date = today - timedelta(days=30)
        elif period == 'last_3months':
            start_date = today - timedelta(days=90)
        else:
            start_date = today - timedelta(days=7)
        return start_date, today

    def get_top_gs_by_ticket_count(self, zone_id=None, period=None):
        """
        Top 10 جایگاه‌های دارای بیشترین تعداد تیکت
        """

        qs = Ticket.objects.all().exclude(organization_id=4)
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.values('gs__name', 'gs__gsid', 'gs__area__zone__name').annotate(
            ticket_count=Count('id')
        ).order_by('-ticket_count')[:10]

    def get_top_failure_types(self, zone_id=None, period=None):
        """
        Top 10 انواع خرابی‌های پرتکرار
        """
        qs = Ticket.objects.all().exclude(organization_id=4)
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.values('failure__info').annotate(
            failure_count=Count('id'),
            avg_resolution_time=Avg(F('closedate') - F('create'))
        ).order_by('-failure_count')[:10]

    def get_top_technicians_by_ticket_count(self, zone_id=None, period=None):
        """
        Top 10 تکنسین‌های فعال بر اساس تعداد تیکت‌های رسیدگی شده
        """
        qs = Workflow.objects.all()
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(createtime__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(ticket__gs__area__zone_id=zone_id)

        return qs.values(
            'user__owner__name',
            'user__owner__lname',
            'user__owner__id'
        ).annotate(
            ticket_count=Count('ticket', distinct=True),
            avg_resolution_time=Avg(F('ticket__closedate') - F('ticket__create'))
        ).order_by('-ticket_count')[:10]

    def get_longest_resolution_tickets(self, zone_id=None, period=None):
        """
        تیکت‌های با بیشترین زمان رسیدگی
        """
        qs = Ticket.objects.filter(status_id=2).exclude(organization_id=4)  # فقط تیکت‌های بسته شده
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.annotate(
            resolution_time=F('closedate') - F('create')
        ).order_by('-resolution_time')[:10]

    def get_pending_tickets(self, zone_id=None, period=None):
        """
        تیکت‌های باز بدون رسیدگی
        """
        qs = Ticket.objects.filter(status_id=1).exclude(organization_id=4)  # فقط تیکت‌های باز
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])
        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.order_by('create')[:10]

    def get_avg_resolution_by_zone(self, period=None):
        """
        میانگین زمان رسیدگی به تیکت‌ها در هر منطقه
        """
        qs = Ticket.objects.filter(status_id=2).exclude(organization_id=4)
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        return qs.values('gs__area__zone__name', 'gs__area__zone__id').annotate(
            avg_resolution=Avg(F('closedate') - F('create')),
            ticket_count=Count('id')
        ).order_by('gs__area__zone__name')

    def get_ticket_count_by_period(self, zone_id=None, period_type='daily'):
        """
        تعداد تیکت‌ها در بازه‌های زمانی مختلف
        """
        qs = Ticket.objects.all()

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        if period_type == 'hourly':
            return qs.annotate(
                hour=ExtractHour('create')
            ).values('hour').annotate(
                count=Count('id')
            ).order_by('hour')

        elif period_type == 'weekly':
            return qs.annotate(
                week=ExtractWeek('create'),
                year=ExtractYear('create')
            ).values('year', 'week').annotate(
                count=Count('id')
            ).order_by('year', 'week')

        else:  # daily
            return qs.annotate(
                day=TruncDate('create')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')

    def get_technicians_fastest_resolution(self, zone_id=None, period=None):
        """
        تکنسین‌هایی با کمترین زمان رسیدگی
        """
        qs = Ticket.objects.filter(status_id=2, actioner__role__role='tek').exclude(organization_id=4)
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.values(
            'actioner__name',
            'actioner__lname',
            'actioner_id'
        ).annotate(
            ticket_count=Count('id'),
            avg_resolution_time=Avg(F('closedate') - F('create'))
        ).order_by('avg_resolution_time')[:10]

    def get_tickets_with_most_workflows(self, zone_id=None, period=None):
        """
        تیکت‌های با بیشترین تعداد پیگیری
        """
        qs = Ticket.objects.annotate(
            workflow_count=Count('workflow')
        ).order_by('-workflow_count')

        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])

        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs[:10]

    def get_lowest_rated_tickets(self, zone_id=None, period=None):
        """
        تیکت‌های با پایین‌ترین امتیاز (star)
        """
        qs = Ticket.objects.filter(star__gt=0).exclude(organization_id=4)  # فقط تیکت‌های دارای امتیاز
        start_date, end_date = self._get_date_range(period)

        if start_date:
            qs = qs.filter(create__date__range=[start_date, end_date])
        if zone_id:
            qs = qs.filter(gs__area__zone_id=zone_id)

        return qs.order_by('star')[:10]  # 10 تیکت با کمترین امتیاز


class TicketAnalysis(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    analysis_type = models.CharField(max_length=50)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TicketAnalysisManager()

    class Meta:
        verbose_name = 'تحلیل تیکت'
        verbose_name_plural = 'تحلیل‌های تیکت'
        ordering = ['-created_at']


class LoginInfo(models.Model):
    image = models.ImageField(upload_to='loginimage/', blank=True, null=True)


class Peykarbandylog(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    nazel = models.CharField(max_length=3, blank=True, null=True)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.gs.gsid


class RequiredFieldsConfig(models.Model):
    FIELD_TYPES = [
        ('foreign_key', 'ForeignKey'),
        ('char_field', 'CharField'),
        ('choice_field', 'ChoiceField'),
    ]

    field_name = models.CharField(blank=True, null=True, max_length=100, verbose_name="نام فیلد")
    field_label = models.CharField(blank=True, null=True, max_length=200, verbose_name="عنوان فیلد")
    field_type = models.CharField(blank=True, null=True, max_length=20, choices=FIELD_TYPES, default='foreign_key',
                                  verbose_name="نوع فیلد")
    forbidden_value = models.TextField(blank=True, null=True, verbose_name="مقدار غیرمجاز (مقادیر را با کاما جدا کنید)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تنظیم فیلد اجباری"
        verbose_name_plural = "تنظیمات فیلدهای اجباری"

    def __str__(self):
        return self.field_label

    def get_forbidden_values(self):
        """تبدیل مقادیر غیرمجاز به لیست"""
        if self.forbidden_value:
            return [v.strip() for v in self.forbidden_value.split(',')]
        return []


class CompanyStatus(models.Model):
    name = models.CharField(max_length=20, verbose_name="شرح")

    def __str__(self):
        return self.name

class SellProduct(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name="نام جایگاه")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="نام فرآورده")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name="نام کاربر")
    send_date = models.DateField(verbose_name="تاریخ ارسال")
    amount = models.PositiveIntegerField(verbose_name="مقدار")
    recive_date = models.DateField(verbose_name="تاریخ رسید", blank=True, null=True)
    price = models.PositiveIntegerField(verbose_name="نرخ هر لیتر")
    status = models.ForeignKey(CompanyStatus, on_delete=models.CASCADE, verbose_name="وضعیت", blank=True, null=True)

    def __str__(self):
        return self.gs, self.owner.company
