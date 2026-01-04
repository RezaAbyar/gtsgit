from django.db import models
from django_jalali.db import models as jmodels

from base.modelmanager import RoleeManager
from base.models import GsModel, Owner, Company, Product
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from datetime import datetime, timedelta
from base.models import Area

class CompanyType(models.Model):
    """نوع شرکت (واردکننده، توزیع‌کننده، جایگاه)"""
    name = models.CharField(max_length=50, verbose_name="نام نوع")
    code = models.CharField(max_length=10, unique=True, verbose_name="کد نوع")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "نوع شرکت"
        verbose_name_plural = "انواع شرکت"


class FuelLicense(models.Model):
    """مجوزهای سوخت شرکت‌ها"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="شرکت")
    license_type = models.CharField(max_length=50, verbose_name="نوع مجوز")
    license_number = models.CharField(max_length=100, unique=True, verbose_name="شماره مجوز")
    issue_date = jmodels.jDateField(verbose_name="تاریخ صدور")
    expiry_date = jmodels.jDateField(verbose_name="تاریخ انقضا")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    document_file = models.FileField(upload_to='fuel_licenses/', blank=True, null=True, verbose_name="فایل مجوز")

    def __str__(self):
        return f"{self.company.name} - {self.license_number}"

    class Meta:
        verbose_name = "مجوز سوخت"
        verbose_name_plural = "مجوزهای سوخت"


class SuperModel(models.Model):
    """مشخصات عرضه کننده"""
    gsid = models.CharField(max_length=50, verbose_name="شناسه عرضه کننده")
    name = models.CharField(max_length=50, verbose_name="نام عرضه کننده")
    address = models.CharField(max_length=50, verbose_name="آدرس")
    phone = models.CharField(max_length=50, verbose_name="تلفن")
    makhzan = models.PositiveSmallIntegerField(verbose_name="ظرفیت مخزن", default=0)
    owner = models.OneToOneField(Owner, on_delete=models.CASCADE, verbose_name="کاربر")
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="انتخاب ناحیه", null=True, blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def str(self):
        return self.name


class Nazel(models.Model):
    """نازل های عرضه کننده"""
    supermodel = models.ForeignKey(SuperModel, on_delete=models.CASCADE, verbose_name="نام عرضه کننده")
    number = models.PositiveSmallIntegerField(verbose_name="شماره نازل")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="نام فرآورده")
    makhzan = models.PositiveSmallIntegerField(verbose_name="شماره مخزن", default=0)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.supermodel.name} - {self.number}"


class UserDistributionProfile(models.Model):
    """پروفایل کاربر برای مشخص کردن نوع و شرکت مربوطه"""
    DISTRIBUTION_ROLES = [
        ('importer', 'واردکننده'),
        ('distributor', 'توزیع‌کننده'),
        ('gas_station', 'جایگاه'),
    ]

    owner = models.OneToOneField(Owner, on_delete=models.CASCADE, related_name='distribution_profile')
    role = models.CharField(max_length=20, choices=DISTRIBUTION_ROLES)
    managed_stations = models.ManyToManyField(  # فیلد جدید برای جایگاه‌های تحت مدیریت
        SuperModel,
        blank=True,
        verbose_name="جایگاه‌های تحت مدیریت",
        related_name='managers',
        help_text="برای کاربران جایگاه: می‌توانند چندین جایگاه را مدیریت کنند"
    )
    active_station = models.ForeignKey(  # فیلد جدید برای جایگاه فعال
        SuperModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="جایگاه فعال فعلی",
        related_name='active_for_users'
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="شرکت مربوطه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.get_full_name()} - {self.get_role_display()}"

    class Meta:
        verbose_name = "پروفایل کاربر توزیع"
        verbose_name_plural = "پروفایل‌های کاربران توزیع"

    @property
    def current_station(self):
        """جایگاه انتخابی فعلی کاربر (برای ذخیره در session)"""
        # این خاصیت برای مدیریت جایگاه انتخاب شده فعلی است
        return None  # در view مدیریت می‌شود

    def get_managed_stations_count(self):
        """تعداد جایگاه‌های تحت مدیریت"""
        return self.managed_stations.count()

    def can_manage_station(self, station):
        """آیا کاربر می‌تواند این جایگاه را مدیریت کند؟"""
        if self.role != 'gas_station':
            return False
        return station in self.managed_stations.all()


class SuperFuelImport(models.Model):
    """ورود بنزین سوپر توسط واردکنندگان"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('distributed', 'توزیع شده'),
        ('cancelled', 'لغو شده'),
    ]

    importer = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        verbose_name="واردکننده",
        limit_choices_to={'distribution_profile__role': 'importer'}
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="شرکت واردکننده")
    import_date = jmodels.jDateField(verbose_name="تاریخ واردات")
    amount_liters = models.PositiveIntegerField(verbose_name="مقدار (لیتر)")
    tracking_number = models.CharField(max_length=50, unique=True, verbose_name="شماره رهگیری واردات")
    document_number = models.CharField(max_length=100, verbose_name="شماره سند واردات")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, related_name='created_imports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.amount_liters} لیتر - {self.import_date}"

    class Meta:
        verbose_name = "ورود بنزین سوپر"
        verbose_name_plural = "ورود بنزین سوپر"
        ordering = ['-import_date']

    @property
    def remaining_amount(self):
        """مقدار باقی‌مانده از این ورودی برای توزیع"""
        distributed = self.distributions.aggregate(
            total=Sum('amount_liters')
        )['total'] or 0
        return self.amount_liters - distributed

    @property
    def is_available_for_distribution(self):
        """آیا برای توزیع موجودی دارد؟"""
        return self.status in ['confirmed', 'distributed'] and self.remaining_amount > 0


class ImportToDistributor(models.Model):
    """توزیع بنزین سوپر از واردکننده به توزیع‌کننده"""
    fuel_import = models.ForeignKey(
        SuperFuelImport,
        on_delete=models.CASCADE,
        related_name='distributions',
        verbose_name="ورودی بنزین"
    )
    distributor = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        verbose_name="توزیع‌کننده",
        limit_choices_to={'distribution_profile__role': 'distributor'}
    )
    distributor_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="شرکت توزیع‌کننده"
    )
    distribution_date = jmodels.jDateField(verbose_name="تاریخ توزیع")
    amount_liters = models.PositiveIntegerField(verbose_name="مقدار توزیع شده (لیتر)")
    price_per_liter = models.PositiveIntegerField(verbose_name="نرخ هر لیتر (ریال)")
    document_number = models.CharField(max_length=100, verbose_name="شماره سند توزیع")
    transport_info = models.CharField(max_length=200, blank=True, verbose_name="اطلاعات حمل")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.distributor_company.name} - {self.amount_liters} لیتر"

    class Meta:
        verbose_name = "توزیع به توزیع‌کننده"
        verbose_name_plural = "توزیع به توزیع‌کننده‌ها"
        ordering = ['-distribution_date']


class DistributorGasStation(models.Model):
    """جایگاه‌های زیرمجموعه هر توزیع‌کننده"""
    distributor = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        verbose_name="توزیع‌کننده",
        limit_choices_to={'distribution_profile__role': 'distributor'}
    )
    gas_station = models.ForeignKey(
        SuperModel,
        on_delete=models.CASCADE,
        verbose_name="جایگاه سوخت"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    start_date = jmodels.jDateField(verbose_name="تاریخ شروع همکاری")
    contract_number = models.CharField(max_length=100, blank=True, verbose_name="شماره قرارداد")
    notes = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "جایگاه توزیع‌کننده"
        verbose_name_plural = "جایگاه‌های توزیع‌کننده‌ها"
        unique_together = ['distributor', 'gas_station']

    def __str__(self):
        return f"{self.distributor.get_full_name()} - {self.gas_station.name}"


class DistributionToGasStation(models.Model):
    """توزیع بنزین سوپر از توزیع‌کننده به جایگاه"""
    STATUS_CHOICES = [
        ('scheduled', 'زمان‌بندی شده'),
        ('in_transit', 'در حال حمل'),
        ('delivered', 'تحویل شده'),
        ('received', 'دریافت شده توسط جایگاه'),  # وضعیت جدید
        ('cancelled', 'لغو شده'),
    ]

    distributor_distribution = models.ForeignKey(
        ImportToDistributor,
        on_delete=models.CASCADE,
        related_name='station_distributions',
        verbose_name="توزیع توزیع‌کننده"
    )
    distributor_gas_station = models.ForeignKey(
        DistributorGasStation,
        on_delete=models.CASCADE,
        verbose_name="جایگاه زیرمجموعه"
    )
    delivery_date = jmodels.jDateField(verbose_name="تاریخ تحویل")
    amount_liters = models.PositiveIntegerField(verbose_name="مقدار تحویلی (لیتر)")
    price_per_liter = models.PositiveIntegerField(verbose_name="نرخ هر لیتر به جایگاه (ریال)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # اطلاعات مربوط به رسید جایگاه
    station_receipt_number = models.CharField(max_length=100, blank=True, verbose_name="شماره رسید جایگاه")
    station_received_date = jmodels.jDateField(null=True, blank=True, verbose_name="تاریخ دریافت در جایگاه")
    station_received_by = models.ForeignKey(
        Owner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="دریافت کننده در جایگاه",
        related_name='received_deliveries'
    )
    station_notes = models.TextField(blank=True, verbose_name="ملاحظات جایگاه")

    # فیلدهای موجود
    delivery_document = models.CharField(max_length=100, blank=True, verbose_name="شماره سند تحویل")
    driver_info = models.CharField(max_length=200, blank=True, verbose_name="اطلاعات راننده")
    vehicle_info = models.CharField(max_length=200, blank=True, verbose_name="اطلاعات وسیله نقلیه")
    received_confirmation = models.BooleanField(default=False, verbose_name="تأیید دریافت")
    received_date = jmodels.jDateField(null=True, blank=True, verbose_name="تاریخ دریافت واقعی")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.distributor_gas_station.gas_station.name} - {self.amount_liters} لیتر"

    class Meta:
        verbose_name = "تحویل به جایگاه"
        verbose_name_plural = "تحویل به جایگاه‌ها"
        ordering = ['-delivery_date']


class FuelStock(models.Model):
    """موجودی بنزین سوپر"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="شرکت")
    total_imported = models.PositiveIntegerField(default=0, verbose_name="کل واردات")
    total_distributed = models.PositiveIntegerField(default=0, verbose_name="کل توزیع شده")
    current_stock = models.PositiveIntegerField(default=0, verbose_name="موجودی فعلی")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "موجودی سوخت"
        verbose_name_plural = "موجودی‌های سوخت"

    def __str__(self):
        return f"{self.company.name} - موجودی: {self.current_stock} لیتر"

    def update_stock(self):
        print(self.company.id)
        """به‌روزرسانی خودکار موجودی"""
        imports = SuperFuelImport.objects.filter(
            company=self.company,
            status__in=['confirmed', 'distributed']
        ).aggregate(total=Sum('amount_liters'))['total'] or 0

        distributed = ImportToDistributor.objects.filter(
            distributor_company=self.company
        ).aggregate(total=Sum('amount_liters'))['total'] or 0

        self.total_imported = imports
        self.total_distributed = distributed
        self.current_stock = imports + distributed
        self.save()


class FuelDistributionReport(models.Model):
    """گزارش‌های توزیع سوخت"""
    report_type = models.CharField(max_length=50, verbose_name="نوع گزارش")
    period_start = jmodels.jDateField(verbose_name="شروع دوره")
    period_end = jmodels.jDateField(verbose_name="پایان دوره")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name="شرکت")
    generated_by = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, verbose_name="تولید کننده")
    report_data = models.JSONField(verbose_name="داده‌های گزارش")
    file_path = models.FileField(upload_to='fuel_reports/', blank=True, null=True, verbose_name="فایل گزارش")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "گزارش توزیع"
        verbose_name_plural = "گزارش‌های توزیع"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} - {self.period_start} تا {self.period_end}"


# ============================
# سیگنال‌ها
# ============================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum


@receiver(post_save, sender=SuperFuelImport)
def update_fuel_stock_on_import(sender, instance, **kwargs):
    """به‌روزرسانی موجودی پس از ثبت ورودی جدید"""
    if instance.status in ['confirmed', 'distributed']:
        stock, created = FuelStock.objects.get_or_create(company=instance.company)
        stock.update_stock()


@receiver(post_save, sender=ImportToDistributor)
@receiver(post_delete, sender=ImportToDistributor)
def update_fuel_stock_on_distribution(sender, instance, **kwargs):
    """به‌روزرسانی موجودی پس از توزیع"""
    stock, created = FuelStock.objects.get_or_create(company=instance.distributor_company)
    stock.update_stock()

    # به‌روزرسانی موجودی واردکننده
    if instance.fuel_import:
        importer_stock, created = FuelStock.objects.get_or_create(
            company=instance.fuel_import.company
        )
        importer_stock.update_stock()


@receiver(post_save, sender=UserDistributionProfile)
def create_user_distribution_profile(sender, instance, created, **kwargs):
    """ایجاد پروفایل توزیع برای کاربران جدید"""
    if created:
        # اگر کاربر نقش توزیع‌کننده دارد، موجودی اولیه ایجاد کن
        if instance.role == 'distributor':
            FuelStock.objects.get_or_create(company=instance.company)
        elif instance.role == 'importer':
            FuelStock.objects.get_or_create(company=instance.company)


@receiver(post_save, sender=SuperFuelImport)
def update_stock_on_import_save(sender, instance, created, **kwargs):
    """
    به‌روزرسانی موجودی پس از ذخیره ورود
    """
    if instance.status in ['confirmed', 'distributed']:
        stock, _ = FuelStock.objects.get_or_create(company=instance.company)
        stock.update_stock()


@receiver(post_delete, sender=SuperFuelImport)
def update_stock_on_import_delete(sender, instance, **kwargs):
    """
    به‌روزرسانی موجودی پس از حذف ورود
    """
    if instance.status in ['confirmed', 'distributed']:
        stock = FuelStock.objects.filter(company=instance.company).first()
        if stock:
            stock.update_stock()


@receiver(post_save, sender=ImportToDistributor)
@receiver(post_delete, sender=ImportToDistributor)
def update_stock_on_distribution(sender, instance, **kwargs):
    """
    به‌روزرسانی موجودی پس از توزیع
    """
    # به‌روزرسانی موجودی توزیع‌کننده
    if instance.distributor_company:
        stock, _ = FuelStock.objects.get_or_create(company=instance.distributor_company)
        stock.update_stock()

    # به‌روزرسانی موجودی واردکننده
    if instance.fuel_import and instance.fuel_import.company:
        importer_stock, _ = FuelStock.objects.get_or_create(
            company=instance.fuel_import.company
        )
        importer_stock.update_stock()


@receiver(post_save, sender=DistributionToGasStation)
@receiver(post_delete, sender=DistributionToGasStation)
def update_stock_on_delivery(sender, instance, **kwargs):
    """
    به‌روزرسانی موجودی پس از تحویل به جایگاه
    """
    # اینجا می‌توانید منطق به‌روزرسانی موجودی جایگاه را اضافه کنید
    # فعلاً فقط لاگ می‌گیریم
    pass


class DirectSaleToDistributor(models.Model):
    """فروش مستقیم واردکننده به توزیع‌کننده"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]

    importer = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        verbose_name="واردکننده",
        limit_choices_to={'distribution_profile__role': 'importer'},
        related_name='direct_sales_as_importer'  # اضافه کردن related_name منحصر به فرد
    )
    distributor = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        verbose_name="توزیع‌کننده",
        limit_choices_to={'distribution_profile__role': 'distributor'},
        related_name='direct_sales_as_distributor'  # اضافه کردن related_name منحصر به فرد
    )
    sale_date = jmodels.jDateField(verbose_name="تاریخ فروش")
    amount_liters = models.PositiveIntegerField(verbose_name="مقدار (لیتر)")
    price_per_liter = models.PositiveIntegerField(verbose_name="نرخ هر لیتر (ریال)")
    total_price = models.PositiveIntegerField(verbose_name="مبلغ کل (ریال)", editable=False)
    document_number = models.CharField(max_length=100, verbose_name="شماره سند فروش")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # محاسبه خودکار مبلغ کل
        self.total_price = self.amount_liters * self.price_per_liter
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.importer} → {self.distributor}: {self.amount_liters} لیتر"

    class Meta:
        verbose_name = "فروش مستقیم به توزیع‌کننده"
        verbose_name_plural = "فروش‌های مستقیم به توزیع‌کننده"


class DailyProductPrice(models.Model):
    """نرخ روزانه فرآورده برای هر عرضه کننده"""
    supermodel = models.ForeignKey(
        SuperModel,
        on_delete=models.CASCADE,
        verbose_name="عرضه کننده",
        related_name='daily_prices'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="فرآورده")
    price_date = jmodels.jDateField(verbose_name="تاریخ نرخ")
    price_per_liter = models.PositiveIntegerField(verbose_name="نرخ هر لیتر (ریال)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "نرخ روزانه فرآورده"
        verbose_name_plural = "نرخ‌های روزانه فرآورده"
        unique_together = ['supermodel', 'product', 'price_date']
        ordering = ['-price_date']

    def __str__(self):
        return f"{self.supermodel.name} - {self.product.name} - {self.price_date}"


class SupplierTankInventory(models.Model):
    """موجودی واقعی مخازن عرضه کننده"""
    supermodel = models.ForeignKey(
        SuperModel,
        on_delete=models.CASCADE,
        verbose_name="عرضه کننده",
        related_name='tank_inventories'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="فرآورده")
    tank_date = jmodels.jDateField(verbose_name="تاریخ ثبت موجودی")
    actual_quantity = models.PositiveIntegerField(verbose_name="مقدار واقعی (لیتر)")
    calculated_quantity = models.PositiveIntegerField(verbose_name="مقدار محاسباتی (لیتر)")
    difference = models.IntegerField(verbose_name="اختلاف", default=0)
    notes = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "موجودی واقعی مخزن"
        verbose_name_plural = "موجودی‌های واقعی مخازن"
        unique_together = ['supermodel', 'product', 'tank_date']
        ordering = ['-tank_date']

    def save(self, *args, **kwargs):
        # محاسبه خودکار اختلاف
        self.difference = self.actual_quantity - self.calculated_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supermodel.name} - {self.product.name} - {self.tank_date}"


class NozzleSale(models.Model):
    """فروش روزانه هر نازل"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('cancelled', 'لغو شده'),
    ]

    supermodel = models.ForeignKey(SuperModel, on_delete=models.CASCADE, verbose_name="عرضه کننده")
    nozzle = models.ForeignKey(Nazel, on_delete=models.CASCADE, verbose_name="نازل")
    sale_date = jmodels.jDateField(verbose_name="تاریخ فروش")
    start_counter = models.PositiveIntegerField(verbose_name="شماره اول وقت")
    end_counter = models.PositiveIntegerField(verbose_name="شماره آخر وقت")
    test_amount = models.PositiveIntegerField(verbose_name="میزان آزمایش (لیتر)", default=0)
    sold_liters = models.PositiveIntegerField(verbose_name="لیتر فروخته شده")
    price_per_liter = models.PositiveIntegerField(verbose_name="نرخ هر لیتر (ریال)")
    total_amount = models.PositiveIntegerField(verbose_name="مبلغ کل (ریال)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "فروش نازل"
        verbose_name_plural = "فروش‌های نازل"
        unique_together = ['nozzle', 'sale_date']
        ordering = ['-sale_date']

    def save(self, *args, **kwargs):
        # محاسبه خودکار لیتر فروخته شده
        if self.end_counter >= self.start_counter:
            raw_liters  = self.end_counter - self.start_counter
        else:
            # اگر شمارشگر ریست شده باشد
            # (فرض: حداکثر شمارشگر 999999)
            max_counter = 999999
            raw_liters = (max_counter - self.start_counter) + self.end_counter

        self.sold_liters = max(0, raw_liters - self.test_amount)

        # محاسبه مبلغ کل
        self.total_amount = self.sold_liters * self.price_per_liter

        return super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nozzle} - {self.sale_date} - {self.sold_liters} لیتر"


class SupplierDailySummary(models.Model):
    """خلاصه روزانه برای هر عرضه کننده"""
    supermodel = models.ForeignKey(SuperModel, on_delete=models.CASCADE, verbose_name="عرضه کننده")
    summary_date = jmodels.jDateField(verbose_name="تاریخ خلاصه")
    total_sales_liters = models.PositiveIntegerField(verbose_name="کل فروش لیتر", default=0)
    total_sales_amount = models.PositiveIntegerField(verbose_name="کل فروش ریال", default=0)
    opening_inventory = models.PositiveIntegerField(verbose_name="موجودی اول روز", default=0)
    closing_inventory = models.PositiveIntegerField(verbose_name="موجودی آخر روز", default=0)
    calculated_closing = models.PositiveIntegerField(verbose_name="موجودی محاسباتی", default=0)
    difference = models.IntegerField(verbose_name="اختلاف", default=0)

    class Meta:
        verbose_name = "خلاصه روزانه عرضه کننده"
        verbose_name_plural = "خلاصه روزانه عرضه کنندگان"
        unique_together = ['supermodel', 'summary_date']
        ordering = ['-summary_date']

    def __str__(self):
        return f"{self.supermodel.name} - {self.summary_date}"


@receiver(post_save, sender=NozzleSale)
def update_supplier_inventory_on_sale(sender, instance, created, **kwargs):
    """به‌روزرسانی موجودی مخزن پس از ثبت فروش نازل"""
    if instance.status == 'confirmed':
        # کسر از موجودی مخزن مربوطه
        _create = True
        try:
            _list = SupplierDailySummary.objects.filter(
                supermodel=instance.supermodel,
                summary_date=instance.sale_date
            ).count()
            if _list > 0:
                _create = False
            # ایجاد یا به‌روزرسانی خلاصه روزانه
            summary, created = SupplierDailySummary.objects.get_or_create(
                supermodel=instance.supermodel,
                summary_date=instance.sale_date
            )

            # اگر خلاصه جدید است، موجودی اول روز را از آخرین موجودی واقعی بگیر
            last_inventory = SupplierTankInventory.objects.get(
                supermodel=instance.supermodel,
                product=instance.nozzle.product
            )
            if last_inventory and _create:
                summary.opening_inventory = last_inventory.actual_quantity

            total_sales_liters = NozzleSale.objects.filter(
                supermodel=instance.supermodel,
                sale_date=instance.sale_date,
                status='confirmed'
            ).aggregate(total=Sum('sold_liters'))['total'] or 0
            if _create:
                last_inventory.actual_quantity -= total_sales_liters
                last_inventory.calculated_quantity -= total_sales_liters
                last_inventory.save()

            # به‌روزرسانی کل فروش‌ها
            summary.total_sales_liters = NozzleSale.objects.filter(
                supermodel=instance.supermodel,
                sale_date=instance.sale_date,
                status='confirmed'
            ).aggregate(total=Sum('sold_liters'))['total'] or 0
            summary.total_sales_amount = NozzleSale.objects.filter(
                supermodel=instance.supermodel,
                sale_date=instance.sale_date,
                status='confirmed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            summary.calculated_closing = summary.opening_inventory - summary.total_sales_liters
            summary.save()
            if not _create:
                last_inventory.actual_quantity = summary.calculated_closing
                last_inventory.calculated_quantity = summary.calculated_closing
                last_inventory.save()

        except Exception as e:
            print(f"Error updating inventory on sale: {e}")


@receiver(post_save, sender=DistributionToGasStation)
def update_supplier_inventory_on_receipt(sender, instance, **kwargs):
    """به‌روزرسانی موجودی مخزن پس از تأیید دریافت توسط جایگاه"""
    if instance.status == 'received' and instance.distributor_gas_station.gas_station:
        # افزایش موجودی مخزن مربوطه
        supermodel = instance.distributor_gas_station.gas_station

        # یافتن محصول مربوطه (فرض: سوپر)
        # در اینجا باید منطق پیدا کردن محصول صحیح را پیاده‌سازی کنید
        try:
            # فرض: اولین نازل برای پیدا کردن محصول
            nozzle = Nazel.objects.filter(supermodel=supermodel).first()
            if nozzle:
                product = nozzle.product

                # به‌روزرسانی خلاصه روزانه
                summary, created = SupplierDailySummary.objects.get_or_create(
                    supermodel=supermodel,
                    summary_date=instance.station_received_date or instance.delivery_date
                )

                # افزایش موجودی اول روز برای روز بعد (اگر دریافت در همان روز باشد)
                # یا افزایش موجودی بسته به منطق کسب‌وکار

        except Exception as e:
            print(f"Error updating inventory on receipt: {e}")


@receiver(post_save, sender=SupplierTankInventory)
def update_daily_summary_on_inventory(sender, instance, created, **kwargs):
    """به‌روزرسانی خلاصه روزانه پس از ثبت موجودی واقعی"""
    if created:
        try:
            summary, created = SupplierDailySummary.objects.get_or_create(
                supermodel=instance.supermodel,
                summary_date=instance.tank_date
            )

            # تنظیم موجودی واقعی آخر روز
            summary.closing_inventory = instance.actual_quantity

            # محاسبه اختلاف
            if summary.calculated_closing > 0:
                summary.difference = instance.actual_quantity - summary.calculated_closing

            summary.save()

            # برای روز بعد، موجودی اول روز را تنظیم کن
            next_day = instance.tank_date + timedelta(days=1)
            next_summary, created = SupplierDailySummary.objects.get_or_create(
                supermodel=instance.supermodel,
                summary_date=next_day
            )

            if created:
                next_summary.opening_inventory = instance.actual_quantity
                next_summary.save()

        except Exception as e:
            print(f"Error updating daily summary on inventory: {e}")


