from django.db import models
from base.models import Owner, Zone, GsModel, Pump, Product
from django.utils import timezone
from django.core.validators import MinValueValidator
from django_jalali.db import models as jmodels
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
import os
from jdatetime import datetime as jdatetime_datetime, date as jdatetime_date
import re


class Sells(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()
    end2 = models.IntegerField(default=0)
    sell = models.IntegerField()
    sell2 = models.IntegerField(default=0)
    total_sell = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tarikh = models.DateField()
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    uniq = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.gs.gsid

    def total_sell(self):
        return self.sell + self.sell2


class SarakKasri(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tarikh_start = models.DateField()
    mojodi_in_check = models.PositiveIntegerField(default=0)
    barname = models.PositiveIntegerField(default=0)
    azmayesh = models.PositiveIntegerField(default=0)
    mojodi_startdore = models.PositiveIntegerField(default=0)
    mojodi_enddore = models.PositiveIntegerField(default=0)
    tarikh = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    uniq = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.gs.name


class SarakKasri2(models.Model):
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tarikh_start = models.DateField()
    mojodi_in_check = models.PositiveIntegerField(default=0)
    barname = models.PositiveIntegerField(default=0)
    azmayesh = models.PositiveIntegerField(default=0)
    mojodi_startdore = models.PositiveIntegerField(default=0)
    mojodi_enddore = models.PositiveIntegerField(default=0)
    tarikh = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    uniq = models.CharField(max_length=20, unique=True)
    tarikhakharindore = models.CharField(max_length=20, blank=True, null=True)
    kasrimojazi = models.PositiveIntegerField(default=0)
    sarakazebteda = models.CharField(max_length=20, blank=True, null=True)
    saraknamojaz = models.CharField(max_length=20, blank=True, null=True)
    sarakmoghayerat = models.CharField(max_length=20, blank=True, null=True)
    sell = models.PositiveIntegerField(default=0)
    sell2 = models.PositiveIntegerField(default=0)
    lastdore = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.gs.name


class CertificateType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام گواهی/مدرک")
    validity_period = models.PositiveIntegerField(
        verbose_name="مدت اعتبار (ماه)",
        validators=[MinValueValidator(1)]
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")


    class Meta:
        verbose_name = "نوع گواهی"
        verbose_name_plural = "انواع گواهی‌ها"

    def __str__(self):
        return self.name

class CBrand(models.Model):
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.CASCADE, verbose_name="نوع گواهی")
    name = models.CharField(max_length=50)
    description = models.TextField()
    status = models.BooleanField(default=False)
    statenumber = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        if ext not in ["jpg","jpeg", "png","pdf"]:
            print(1)
            raise ValidationError(f"invalid image extension: {filename}")

        filename = f"{unique_id}.{ext}"
        return os.path.join("certificates/%Y/%m/%d/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 500
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 500
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name="جایگاه", related_name='certificates')
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.CASCADE, verbose_name="نوع گواهی")
    issue_date = jmodels.jDateField(verbose_name="تاریخ صدور")
    expiry_date = jmodels.jDateField(verbose_name="تاریخ انقضا", blank=True, null=True)
    document = models.FileField(upload_to=wrapper, verbose_name="فایل مدرک", validators=[validate_image])
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="آپلود کننده")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ آپلود")
    cbrand = models.ForeignKey(CBrand, on_delete=models.CASCADE,blank=True, null=True)

    class Meta:
        verbose_name = "گواهی جایگاه"
        verbose_name_plural = "گواهی‌های جایگاه‌ها"
        ordering = ['expiry_date']

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.issue_date and self.certificate_type:
            # محاسبه خودکار تاریخ انقضا بر اساس مدت اعتبار
            self.expiry_date = self.issue_date + timezone.timedelta(
                days=30 * self.certificate_type.validity_period
            )
        super().save(*args, **kwargs)

    def is_expired(self):
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date

    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    def __str__(self):
        return f"{self.gs.name} - {self.certificate_type.name}"

    @property
    def validity_days(self):
        """محاسبه مدت اعتبار به روز"""
        if self.expiry_date and self.issue_date:
            return (self.expiry_date - self.issue_date).days
        return None





    def get_related_certificates(self):
        """دریافت مدارک مرتبط (همان نوع برای همان جایگاه)"""
        return Certificate.objects.filter(
            gs=self.gs,
            certificate_type=self.certificate_type
        ).exclude(id=self.id).order_by('-issue_date')


class CertificateAlert(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, verbose_name="گواهی")
    alert_date = models.DateTimeField(verbose_name="تاریخ هشدار")
    is_sent = models.BooleanField(default=False, verbose_name="ارسال شده")
    message = models.TextField(blank=True, verbose_name="متن پیام")

    class Meta:
        verbose_name = "هشدار انقضا"
        verbose_name_plural = "هشدارهای انقضا"

    def __str__(self):
        return f"هشدار برای {self.certificate}"


class EmergencyPermission(models.Model):

    plate_number = models.CharField(max_length=20, verbose_name='شماره پلاک')
    plate_number1 = models.PositiveSmallIntegerField(null=True, blank=True)
    plate_number2 = models.PositiveSmallIntegerField(null=True, blank=True)
    plate_number3 = models.PositiveSmallIntegerField(null=True, blank=True)
    liters = models.PositiveIntegerField(verbose_name='لیتراژ مجاز')
    station_name = models.ForeignKey(GsModel,on_delete=models.CASCADE,blank=True, null=True , verbose_name='نام جایگاه')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE,blank=True, null=True, verbose_name='صادر کننده مجوز')
    created_at = models.DateField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    used = models.BooleanField(default=False, verbose_name='استفاده شده')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ استفاده')
    expired_date = models.DateField(blank=True, null=True, verbose_name='تاریخ انقضا مجوز')

    class Meta:
        verbose_name = 'مجوز اضطراری'
        verbose_name_plural = 'مجوزهای اضطراری'

    def __str__(self):
        return f"{self.plate_number} - {self.station_name} - {self.liters}L"


class EmergencyFueling(models.Model):
    station_name = models.ForeignKey(GsModel, on_delete=models.CASCADE, verbose_name='نام جایگاه',blank=True, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE,blank=True, null=True, verbose_name='کاربر')
    plate_number = models.CharField(max_length=20, verbose_name='شماره پلاک')
    plate_number1 = models.PositiveSmallIntegerField(null=True, blank=True)
    plate_number2 = models.PositiveSmallIntegerField(null=True, blank=True)
    plate_number3 = models.PositiveSmallIntegerField(null=True, blank=True)
    liters = models.PositiveIntegerField(verbose_name='لیتراژ تحویلی')
    fueling_date = models.DateField(default=timezone.now, verbose_name='تاریخ سوختگیری')
    permission = models.ForeignKey(
        EmergencyPermission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='مجوز استفاده شده'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        verbose_name = 'سوخت‌گیری اضطراری'
        verbose_name_plural = 'سوخت‌گیری‌های اضطراری'
        ordering = ['-created_at']

    # def clean(self):
    #     # فقط زمانی اعتبارسنجی کن که مجوزی انتخاب نشده (فاقد مجوز)
    #     if not self.permission:
    #         # اعتبارسنجی شماره پلاک ایرانی
    #
    #
    #         # بررسی سوخت‌گیری تکراری در همان روز
    #         same_day_fueling = EmergencyFueling.objects.filter(
    #             plate_number=self.plate_number,
    #             fueling_date=self.fueling_date
    #         ).exclude(pk=self.pk)
    #
    #         if same_day_fueling.exists():
    #             raise ValidationError('این پلاک در تاریخ امروز در جایگاه دیگری سوختگیری داشته است')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        # اگر از مجوز استفاده شده، آن را علامتگذاری کن
        if self.permission and not self.permission.used:
            self.permission.used = True
            self.permission.used_at = timezone.now()
            self.permission.save()

    def validate_iranian_plate(self, plate):
        # الگوی پلاک ایرانی
        pattern = r'^[0-9]{2}[آ-ی]{1}[0-9]{3}[0-9]{2}$|^[0-9]{2}[آ-ی]{1}[0-9]{2}[0-9]{3}$'
        return re.match(pattern, plate) is not None

    def get_jalali_date(self):
        return jdatetime_date.fromgregorian(date=self.fueling_date)

    def __str__(self):
        return f"{self.plate_number} - {self.station} - {self.liters}L"