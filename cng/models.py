from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import Zone, Area, City


# جدول مرجع - ظرفیت‌ها
class Capacity(models.Model):
    value = models.PositiveIntegerField(unique=True, verbose_name="ظرفیت (مترمکعب بر ساعت)")

    def __str__(self):
        return f"{self.value}"

    class Meta:
        verbose_name = "ظرفیت"
        verbose_name_plural = "ظرفیت‌ها"


class EquipmentSupplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام تأمین‌کننده")
    code = models.CharField(max_length=10, unique=True, verbose_name="کد")

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "تأمین‌کننده تجهیزات"
        verbose_name_plural = "تأمین‌کنندگان تجهیزات"


# مدل اصلی جایگاه
class CNGStation(models.Model):
    # کد 7 رقمی: XXYYZZZ
    code = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="کد جایگاه",
        validators=[MinValueValidator(1000000), MaxValueValidator(9999999)]
    )
    old_code = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="کد قدیمی جایگاه"
    )
    name = models.CharField(max_length=200, verbose_name="نام جایگاه")
    owner_name = models.CharField(max_length=200, blank=True, verbose_name="نام جایگاه دار")

    # حوزه (منطقه جغرافیایی)
    ZONE_CHOICES = [
        ('غرب', 'غرب'),
        ('شرق', 'شرق'),
        ('جنوب', 'جنوب'),
        ('شمال', 'شمال'),
        ('مرکز', 'مرکز'),
    ]
    region = models.CharField(max_length=10, choices=ZONE_CHOICES, verbose_name="حوزه")

    # ارتباط با مدل‌های پایه
    zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        verbose_name="منطقه",
        related_name='cng_stations'
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        verbose_name="ناحیه",
        related_name='cng_stations'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name="شهر",
        related_name='cng_stations'
    )

    # وضعیت مالکیت
    OWNERSHIP_CHOICES = [
        ('تك منظوره خصوصي', 'تک منظوره خصوصی'),
        ('تك منظوره صنايع دفاع', 'تک منظوره صنایع دفاع'),
        ('تك منظوره غير خصوصي', 'تک منظوره غیر خصوصی'),
        ('دو منظوره خصوصي', 'دو منظوره خصوصی'),
        ('دو منظوره شركتي', 'دو منظوره شرکتی'),
        ('دو منظوره صنايع دفاع', 'دو منظوره صنایع دفاع'),
        ('دومنظوره غير خصوصي', 'دومنظوره غیر خصوصی'),
    ]
    ownership_status = models.CharField(
        max_length=30,
        choices=OWNERSHIP_CHOICES,
        verbose_name="وضعیت مالکیت"
    )

    address = models.TextField(verbose_name="آدرس جایگاه")

    # پیشرفت تولید تجهیزات (True = تجهیز در جایگاه وجود دارد)
    equipment_progress = models.BooleanField(
        default=False,
        verbose_name="پیشرفت تولید تجهیزات"
    )

    # اطلاعات زمانی
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    def generate_station_code(self):
        """تولید خودکار کد جایگاه بر اساس کد منطقه و ناحیه"""
        if self.zone and self.area:
            zone_code = str(self.zone.zoneid).zfill(2)
            area_code = str(self.area.areaid).zfill(2)

            # پیدا کردن آخرین کد در این ناحیه
            last_station = CNGStation.objects.filter(
                code__startswith=f"{zone_code}{area_code}"
            ).order_by('-code').first()

            if last_station:
                last_serial = int(str(last_station.code)[-3:])
                new_serial = last_serial + 1
            else:
                new_serial = 1

            serial_code = str(new_serial).zfill(3)
            return int(f"{zone_code}{area_code}{serial_code}")
        return None

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_station_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "جایگاه CNG"
        verbose_name_plural = "جایگاه‌های CNG"
        ordering = ['code']


# مدل تجهیزات
class Equipment(models.Model):
    station = models.ForeignKey(
        CNGStation,
        on_delete=models.CASCADE,
        verbose_name="جایگاه",
        related_name='equipments'
    )
    equipment_code = models.PositiveIntegerField(verbose_name="کد تجهیز")
    contract_number = models.CharField(max_length=100, verbose_name="قرارداد تجهیز")
    dispenser_count = models.PositiveIntegerField(default=1, verbose_name="تعداد دیسپنسر")

    supplier = models.ForeignKey(
        EquipmentSupplier,
        on_delete=models.PROTECT,
        verbose_name="سازنده تجهیز"
    )

    capacity = models.ForeignKey(
        Capacity,
        on_delete=models.PROTECT,
        verbose_name="ظرفیت (مترمکعب بر ساعت)"
    )

    # فشار گاز ورودی
    PRESSURE_CHOICES = [
        (1, '1'),
        (60, '60'),
        (250, '250'),
        (750, '750'),
    ]
    input_pressure = models.PositiveIntegerField(
        choices=PRESSURE_CHOICES,
        verbose_name="فشار گاز ورودی"
    )

    # تاریخ‌ها
    installation_date = models.DateField(verbose_name="تاریخ راه‌اندازی")
    temporary_delivery_date = models.DateField(verbose_name="تاریخ تحویل موقت")
    permanent_delivery = models.BooleanField(default=False, verbose_name="تحویل دائم شده")
    permanent_delivery_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ تحویل دائم"
    )

    # وضعیت تجهیز
    STATUS_CHOICES = [
        ('در حال ساخت', 'در حال ساخت'),
        ('راه اندازي شده تاييد نشده', 'راه‌اندازی شده تأیید نشده'),
        ('راه اندازي شده', 'راه‌اندازی شده'),
        ('جمع آوري شده', 'جمع‌آوری شده'),
        ('حذف شده', 'حذف شده'),
    ]
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        verbose_name="وضعیت"
    )

    # وضعیت حمل تجهیز
    TRANSPORT_CHOICES = [
        ('جايگاه', 'جایگاه'),
        ('منطقه', 'منطقه'),
    ]
    transport_status = models.CharField(
        max_length=10,
        choices=TRANSPORT_CHOICES,
        verbose_name="وضعیت حمل تجهیز"
    )

    # اطلاعات اولویت ارسال
    priority_letter_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نامه اولویت ارسال"
    )
    priority_letter_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ نامه اولویت ارسال"
    )
    priority = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10)],
        verbose_name="اولویت ارسال"
    )

    # اطلاعات حذف
    removal_reason = models.TextField(blank=True, verbose_name="علت حذف")
    removal_letter_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره نامه حذف"
    )
    removal_letter_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ نامه حذف"
    )

    # تجهیز کارکرده
    used_equipment = models.BooleanField(default=False, verbose_name="تجهیز کارکرده")

    # اطلاعات نامه شروع
    start_letter_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره نامه شروع"
    )
    start_letter_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ نامه شروع"
    )

    # کاربری
    USAGE_CHOICES = [
        ('سواري', 'سواری'),
        ('اتوبوسي', 'اتوبوسی'),
        ('اتوبوسي-سواري', 'اتوبوسی-سواری'),
        ('ايستگاه مادر-دختر', 'ایستگاه مادر-دختر'),
    ]
    usage_type = models.CharField(
        max_length=20,
        choices=USAGE_CHOICES,
        verbose_name="کاربری"
    )

    # واگذاری
    transfer_letter_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره نامه واگذاری"
    )
    transfer_letter_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ نامه واگذاری"
    )
    non_private_transferred = models.BooleanField(
        default=False,
        verbose_name="غیرخصوصی واگذارشده"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"تجهیز {self.equipment_code} - {self.station.name}"

    class Meta:
        verbose_name = "تجهیز"
        verbose_name_plural = "تجهیزات"


# مدل میترهای جایگاه
class StationMeter(models.Model):
    station = models.ForeignKey(
        CNGStation,
        on_delete=models.CASCADE,
        verbose_name="جایگاه",
        related_name='meters'
    )
    meter_number = models.CharField(max_length=20, verbose_name="شماره میتر (اشتراک گاز)")

    # نوع کارمزد
    FEE_TYPE_CHOICES = [
        (1, 'جایگاه‌های غیرخصوصی با تجهیزات دولتی'),
        (2, 'جایگاه‌های خصوصی با تجهیزات دولتی'),
        (3, 'جایگاه‌های سرمایه‌گذاری خصوصی سایر شهرها'),
        (4, 'جایگاه‌های سرمایه‌گذاری خصوصی کلان شهرها'),
    ]
    fee_type = models.PositiveIntegerField(
        choices=FEE_TYPE_CHOICES,
        verbose_name="نوع کارمزد"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"متر {self.meter_number} - {self.station.name}"

    class Meta:
        verbose_name = "متر جایگاه"
        verbose_name_plural = "مترهای جایگاه"
