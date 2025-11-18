# stations/models.py
from django.db import models
from django.contrib.auth import get_user_model

from base.models import GsModel, Owner, Ipc, Modem, Operator, ThinClient

User = get_user_model()


class PMChecklist(models.Model):
    station = models.ForeignKey(GsModel, on_delete=models.CASCADE, related_name='checklists', verbose_name="جایگاه")
    technician = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, verbose_name="تکنسین")
    check_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ بررسی")
    next_check_date = models.DateTimeField(verbose_name="تاریخ بررسی بعدی")

    # مشخصات جایگاه
    region = models.CharField(max_length=100, blank=True,null=True, verbose_name="ناحیه")
    area = models.CharField(max_length=100, blank=True,null=True, verbose_name="منطقه")
    owner_phone = models.CharField(max_length=20, blank=True,null=True, verbose_name="شماره همراه مالک")
    operator_phone = models.CharField(max_length=20, blank=True,null=True, verbose_name="شماره همراه اپراتور")
    station_phones = models.CharField(max_length=100, blank=True,null=True, verbose_name="شماره تلفن‌های جایگاه")

    # تجهیزات دفتر جایگاه
    rack_sealed = models.BooleanField(default=False, verbose_name="آیا همه درب‌های رک پلمب شده است؟")
    unsealed_doors = models.TextField(blank=True,null=True, verbose_name="درب‌های بدون پلمب")
    rack_model = models.CharField(max_length=100, blank=True,null=True, verbose_name="مدل رک")
    rack_height = models.CharField(max_length=10, blank=True,null=True, verbose_name="ارتفاع رک")
    rack_temperature = models.CharField(max_length=10, blank=True,null=True, verbose_name="دمای داخل رک")
    ventilation_working = models.BooleanField(default=False, verbose_name="آیا فن‌های تهویه سقف رک کار می‌کنند؟")
    rack_layout_ok = models.BooleanField(default=False, verbose_name="آیا چیدمان داخل رک مطلوب است؟")
    labeling_ok = models.BooleanField(default=False, verbose_name="آیا لیبل گذاری پیچ پنل به صورت صحیح انجام شده؟")
    extra_equipment = models.BooleanField(default=False, verbose_name="آیا تجهیزات اضافی اطراف یا داخل رک وجود دارد؟")

    # اطلاعات سرور
    ipc = models.ForeignKey(Ipc, on_delete=models.CASCADE, blank=True,null=True, verbose_name="مدل ipc")
    server_os_version = models.CharField(max_length=100, blank=True,null=True, verbose_name="نسخه سیستم عامل سرور")
    ram_size = models.CharField(max_length=50, blank=True,null=True, verbose_name="حافظه RAM")
    hdd_size = models.CharField(max_length=50, blank=True,null=True, verbose_name="حجم HDD")
    battry = models.CharField(max_length=10, blank=True,null=True, verbose_name="ولتاژ باتری مادربرد")

    modem = models.ForeignKey(Modem, on_delete=models.CASCADE, blank=True,null=True, verbose_name="مدل مودم")
    modem_type = models.CharField(max_length=50, blank=True,null=True, verbose_name="نوع مودم")
    sim_card_serialnumber = models.CharField(max_length=50, blank=True,null=True, verbose_name="سریال سیم کارت")
    sim_card_number = models.CharField(max_length=50, blank=True,null=True, verbose_name="شماره سیم کارت")
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, verbose_name="اپراتور")
    signal_strength = models.CharField(max_length=50, blank=True,null=True, verbose_name="قدرت سیگنال")

    switch_type = models.CharField(max_length=50, blank=True,null=True, verbose_name="نوع سوئیچ")
    switch_count = models.PositiveIntegerField(default=0, verbose_name="تعداد سوئیچ")
    switch_port = models.PositiveIntegerField(default=0, verbose_name="تعداد پورت")
    switch_connected = models.BooleanField(default=False, verbose_name="آیا سوئیچ بانک به سوئیچ سامانه متصل است؟")


    thinclient_model = models.ForeignKey(ThinClient, on_delete=models.CASCADE, blank=True,null=True, verbose_name="مدل تین کلاینت")
    is_software = models.BooleanField(default=False, verbose_name="آیا سخت افزار و نرم افزار غیر ضروری بر روی تین کلاینت نصب است؟")
    info_software = models.TextField(blank=True,null=True, verbose_name="در صورت وجود توضیح داده شود:")
    print_ok = models.BooleanField(default=False, verbose_name="تنظیمات چاپ انجام شده و گزارشات بدرستی چاپ میشود؟")

    mouse= models.CharField(max_length=10, blank=True,null=True, verbose_name="Mouse")
    mouse_status =models.BooleanField(default=False, verbose_name="mouse سالم است")

    monitor = models.CharField(max_length=10, blank=True,null=True, verbose_name="monitor")
    monitor_status = models.BooleanField(default=False, verbose_name="monitor سالم است")

    printer = models.CharField(max_length=10, blank=True,null=True, verbose_name="printer")
    printer_status = models.BooleanField(default=False, verbose_name="printer سالم است")

    sam_color = models.CharField(max_length=10, blank=True,null=True, verbose_name="رنگ سم ریدر")
    active_sam = models.BooleanField(default=False, verbose_name="سم فعال است")
    active_sam_reader = models.BooleanField(default=False, verbose_name="سم ریدر فعال است")

    switch_cables = models.BooleanField(default=False, verbose_name="آیا کابل های افزایش VGA  و USB متصل به سرور از داخل رک به بیرون کشیده شده است؟")
    bios_password = models.BooleanField(default=False, verbose_name="آیا رمز عبور بایوس ست شده است")
    camera = models.BooleanField(default=False, verbose_name="آیا دوربین مدار بسته به سمت تجهیزات سامانه با قابلیت ذخیره سازی 2 ماه وجود دارد؟")
    active_gs = models.BooleanField(default=False, verbose_name="آیا نرم افزار GS  فعال میباشد")
    active_gds = models.BooleanField(default=False, verbose_name="آیا نرم افزار GDS  فعال میباشد")

    is_phone = models.BooleanField(default=False, verbose_name="آیا خط تلفن وجود دارد")
    is_phone_no_connection = models.BooleanField(default=False, verbose_name="آیا خط تلفن  بدون اتصال به سامانه فعال میباشد")
    is_fibre = models.BooleanField(default=False, verbose_name="آیا در جایگاه فیبر نوری وجود دارد؟")
    # وضعیت UPS
    ups_model= models.CharField(max_length=100,blank=True,null=True, verbose_name="مدل ups")
    has_ups = models.BooleanField(default=False, verbose_name="آیا تجهیزات سامانه هوشمند UPS دارد؟")
    ups_working = models.BooleanField(default=False, verbose_name="آیا UPS عملکرد صحیحی دارد؟")
    ups_backup_time = models.PositiveIntegerField(default=0, verbose_name="زمان پشتیبانی UPS (دقیقه)")
    ups_battery_type = models.CharField(max_length=50, blank=True,null=True, verbose_name="نوع باطری")
    ups_kva = models.CharField(max_length=50, blank=True,null=True, verbose_name="ظرفیت UPS (KVA)")
    ups_valid_support = models.BooleanField(default=False, verbose_name="آیا UPS قرارداد معتبر پشتیبانی دارد؟")
    ups_only_for_system = models.BooleanField(default=False, verbose_name="آیا UPS فقط به سیستم سامانه متصل است؟")

    # وضعیت برق و ارت
    has_separate_ground = models.BooleanField(default=False, verbose_name="چاه ارت مجزای سامانه هوشمند سوخت")
    ground_voltage = models.FloatField(default=0, verbose_name="اختلاف ولتاژ فاز و ارت (ولت)")
    ground_moghavemat = models.FloatField(default=0, verbose_name="مقاومت الکتریکی چاه ارت (اهم)")
    last_ground_renewal = models.DateField( blank=True,null=True, verbose_name="تاریخ آخرین احیاء چاه ارت")
    electrical_panel_ok = models.BooleanField(default=False, verbose_name="آیا تابلوی برق و کابل کشی مناسب است؟")
    circuit_breaker_before_ups = models.BooleanField(default=False, verbose_name="آیا قطع کن قبل از UPS وجود دارد؟")
    is_shine = models.BooleanField(default=False, verbose_name="وظعیت شینه ارت در تابلوی برق مطلوب است؟")
    is_badane = models.BooleanField(default=False, verbose_name="اتصال بدنه تابلوهای فرعی به ارت مطلوب است؟")
    is_ert = models.BooleanField(default=False, verbose_name="وضعیت اتصال به زمین  مطلوب است؟")
    # سایر اطلاعات
    unnecessary_software = models.BooleanField(default=False, verbose_name="آیا نرم افزار غیرضروری نصب است؟")
    unnecessary_software_desc = models.TextField(blank=True,null=True, verbose_name="توضیحات نرم افزارهای غیرضروری")
    printing_configured = models.BooleanField(default=False, verbose_name="تنظیمات چاپ انجام شده است؟")

    notes = models.TextField(blank=True,null=True, verbose_name="یادداشت‌ها")

    inspector_signature = models.CharField(max_length=100, blank=True,null=True, verbose_name="امضاء بازدید کننده")
    station_signature = models.CharField(max_length=100, blank=True,null=True, verbose_name="مهر و امضاء جایگاه")
    smart_system_signature = models.CharField(max_length=100, blank=True,null=True, verbose_name="امضاء رئیس سامانه هوشمند")

    def __str__(self):
        return f"چک لیست PM برای {self.station.name} - {self.check_date}"
