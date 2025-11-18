import os
from django.utils.crypto import get_random_string
import uuid
from PIL import Image
from django.db import IntegrityError
from django.db import models
from jalali.Jalalian import JDate
from api.utils.exception_helper import BadRequest
from base.models import Owner, Mount, Zone, GsModel, Storage, Pump
from django.contrib.auth.models import User
import jdatetime
import datetime
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django_jalali.db import models as jmodels
from base.modelmanager import RoleeManager
from django.db.models.signals import post_save
from django.db.models import Count, Avg, Sum, Q, Max, Case, When, IntegerField, Value
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import re
from django.core.validators import MinValueValidator, MaxValueValidator

_datetemplate = "%Y-%m-%d %H:%M:%S"
_shamsitemplate = 'l j E  Y'
_shamsitemplate2 = 'Y/m/d'


class PayBaseParametrs(models.Model):
    name = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0, blank=True)
    price = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    group = models.PositiveIntegerField(blank=True)
    isshow = models.BooleanField(default=True)
    is_auto = models.BooleanField(default=False)
    enname = models.CharField(max_length=100, blank=True)
    sortable = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return self.name


class Payroll(models.Model):
    tek = models.ForeignKey(Owner, on_delete=models.CASCADE)
    paybaseparametrs = models.ForeignKey(PayBaseParametrs, on_delete=models.CASCADE)
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    price = models.PositiveIntegerField(default=0)
    price2 = models.PositiveIntegerField(default=0)
    create = models.DateTimeField(auto_now_add=True, blank=True)
    update = models.DateTimeField(auto_now=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    accept = models.BooleanField(default=False)
    acceptupdate = models.DateTimeField(blank=True)
    accepttedad = models.PositiveIntegerField(default=0)
    acceptpay = models.BooleanField(default=False)
    acceptupdatepay = models.CharField(blank=True, max_length=10)
    mablagh = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return self.tek.name + " " + self.tek.lname

    def pdate(self):
        jd = JDate(self.acceptupdate.strftime(_datetemplate))
        newsdate = jd.format('l j E  Y H:i')
        return newsdate


class Tektaeed(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    accepttedad = models.BooleanField(default=False)

    def __str__(self):
        return self.zone.name


class PayItems(models.Model):
    paybase = models.ForeignKey(PayBaseParametrs, on_delete=models.CASCADE)
    info = models.CharField(max_length=100)
    storage = models.BooleanField(default=False)
    ename = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.info


class TekKarkard(models.Model):
    tek = models.ForeignKey(Owner, on_delete=models.CASCADE)
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    value = models.IntegerField()
    mozd_sanavat = models.BigIntegerField(blank=True)
    Dastmozd_rozane = models.BigIntegerField(blank=True)
    hoghogh_paye = models.BigIntegerField(blank=True)
    ayabzahab = models.BigIntegerField(blank=True)
    sabeghe = models.PositiveIntegerField(blank=True)
    khodro = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(str(self.period.mount) + ' ' + str(self.tek))

    @classmethod
    def get_karkard(cls, value: int, period: int, tekid: int, kilometr: int):
        try:
            cls.objects.get(period_id=period, tek_id=tekid).delete()
        except cls.DoesNotExist:
            pass
        try:
            owner = Owner.objects.get(id=tekid)
            if not owner.start_date:
                raise BadRequest('تاریخ آغاز بکار ثبت نشده')
            start_date = owner.start_date.split("/")
            start_date = jdatetime.date(day=int(start_date[2]), month=int(start_date[1]),
                                        year=int(start_date[0])).togregorian()
            today = datetime.today()
            d1 = date(year=today.year, month=today.month, day=today.day)
            d2 = date(year=start_date.year, month=start_date.month, day=start_date.day)
            active_year = relativedelta(d1, d2).years

            m_sanavati = MozdSanavat.objects.get(group=owner.job_group, sabeghe=active_year).price
            # int(active_year) * int(settings.PAYROLL_ADD_SABEGHE_IN_YEAR_7GROUP)
            pay = PersonPayment.objects.filter(owner_id=tekid, baseparametr__enname='paye').last()
            if pay:
                d_roozane = m_sanavati + pay.price
            else:
                pay = PayBaseParametrs.objects.get(enname='paye')
                d_roozane = m_sanavati + pay.price
            droozane = pay.price * value
            mount_mozd = d_roozane * value

            # pay = PersonPayment.objects.filter(owner_id=tekid, baseparametr__enname='ayabzahab').last()
            # ayabzahab = (droozane * pay.baseparametr.count) / 100
            cls.objects.create(tek_id=tekid, period_id=period, value=value, mozd_sanavat=m_sanavati, khodro=kilometr,
                               Dastmozd_rozane=d_roozane, sabeghe=active_year,
                               hoghogh_paye=mount_mozd, ayabzahab=0)

            return cls, False
        except cls.DoesNotExist:
            raise BadRequest('این تکنسین وجود ندارد')


class PayParametr(models.Model):
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, blank=True, null=True)
    tek = models.ForeignKey(Owner, on_delete=models.CASCADE, blank=True, null=True)
    payitem = models.ForeignKey(PayItems, on_delete=models.CASCADE)
    inputval = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    create = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniq = models.CharField(blank=True, unique=True, max_length=30)

    def __str__(self):
        return str(self.period.mount)


class InsertPayParametr(models.Model):
    payparametr = models.ForeignKey(PayParametr, on_delete=models.CASCADE)
    tek = models.ForeignKey(Owner, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tek.lname


class PayDarsadMah(models.Model):
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    zaribfani = models.PositiveIntegerField()
    zaribetlaf = models.PositiveIntegerField()
    zaribbahrevari = models.PositiveIntegerField()
    nazels = models.PositiveIntegerField(default=0)
    tickets = models.PositiveIntegerField(default=0)
    rotbe = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    uniq = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.zone.name


class StatusRef(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class StatusStore(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Post(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Store(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    tarikh = models.DateField()
    pinpad = models.PositiveIntegerField(default=0)
    master = models.PositiveIntegerField(default=0)
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True, blank=True)
    marsole = models.CharField(max_length=25, blank=True)
    marsole_date = models.DateTimeField(blank=True)
    resid_date = models.DateTimeField(blank=True)
    in_zone_date = models.DateTimeField(blank=True)
    storage = models.ForeignKey(Storage, blank=True, null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)
    alert72 = models.BooleanField(default=False)
    resid_year = models.CharField(max_length=4, blank=True)
    resid_month = models.CharField(max_length=2, blank=True)
    resid_day = models.CharField(max_length=2, blank=True)
    send_master = models.PositiveIntegerField(default=0)
    send_pinpad = models.PositiveIntegerField(default=0)
    priority = models.PositiveIntegerField(default=0)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.tarikh)

    @classmethod
    def add_or_remove_store(cls, st: int, status: bool, id: int):
        store = cls.objects.get(id=id)
        if st == 1:
            if status:
                store.send_master += 1
            else:
                store.send_master -= 1
        else:
            if status:
                store.send_pinpad += 1
            else:
                store.send_pinpad -= 1
        store.save()

    def pdate(self):
        jd = JDate(self.create.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate

    def mdate(self):
        if self.marsole_date:
            jd = JDate(self.marsole_date.strftime(_datetemplate))
            newsdate = jd.format('l j E  Y  -  H:i')
            return newsdate
        return False

    def rdate(self):
        if self.resid_date:
            jd = JDate(self.resid_date.strftime(_datetemplate))
            newsdate = jd.format('l j E  Y  -  H:i')
        else:
            newsdate = 'دستی رسید شد'
        return newsdate

    def normal_date(self):
        jd = JDate(self.create.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def normal_date_resid(self):
        jd = JDate(self.resid_date.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def get_date_diff(self):
        if self.resid_date:
            t1 = date(year=self.marsole_date.year, month=self.marsole_date.month, day=self.marsole_date.day)
            t2 = date(year=self.resid_date.year, month=self.resid_date.month, day=self.resid_date.day)
            return (t2 - t1).days

    def get_takhsisdate_diff(self):
        if self.resid_date:
            t1 = date(year=self.tarikh.year, month=self.tarikh.month, day=self.tarikh.day)
            t2 = date(year=self.resid_date.year, month=self.resid_date.month, day=self.resid_date.day)
            return (t2 - t1).days


def convert_persian_to_english_digits(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian_digit, english_digit in persian_to_english.items():
        text = text.replace(persian_digit, english_digit)
    return text


# تابع اعتبارسنجی برای بررسی سریال
def validate_serial_number(value):
    # تبدیل اعداد فارسی به انگلیسی
    cleaned_value = convert_persian_to_english_digits(value)
    # حذف خط فاصله و اسپیس
    cleaned_value = re.sub(r'[- ]', '', cleaned_value)
    # بررسی اینکه فقط شامل اعداد انگلیسی باشد
    if not re.match(r'^[0-9]+$', cleaned_value):
        raise ValidationError('شماره سریال فقط باید شامل اعداد انگلیسی باشد و نباید حاوی خط فاصله یا اسپیس باشد.')
    return cleaned_value  # برای ذخیره‌سازی مقدار اصلاح‌شده


class StoreList(models.Model):
    serial = models.CharField(max_length=20, validators=[validate_serial_number], )
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE)
    statusstore = models.ForeignKey(StatusStore, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    getuser = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE, null=True, blank=True)
    update = models.DateTimeField(auto_now=True)
    create = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, null=True, blank=True)
    uniq = models.CharField(max_length=20, null=True, blank=True, unique=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)
    oldserial = models.CharField(max_length=20, null=True, blank=True)
    boardserial = models.CharField(max_length=40, null=True, blank=True)
    info = models.CharField(max_length=500, null=True, blank=True)
    assignticket = models.PositiveIntegerField(null=True, blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.serial

    def pdate(self):
        jd = JDate(self.update.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate

    def normal_date(self):
        jd = JDate(self.update.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate

    def normal_datetime(self):
        jd = JDate(self.update.strftime(_datetemplate))
        newsdate = jd.format('Y/n/j  (H:i)')
        return newsdate


class StoreHistory(models.Model):
    store = models.ForeignKey(StoreList, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    baseroot = models.PositiveIntegerField(blank=True, null=True)
    residroot = models.PositiveIntegerField(default=0)
    information = models.CharField(max_length=100, blank=True)
    starterror = models.BooleanField(default=False)
    isok = models.PositiveIntegerField(default=1)
    imgid = models.ForeignKey("ImgSerial", on_delete=models.CASCADE, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    activeday = models.PositiveIntegerField(null=True, blank=True)
    activeclass = models.CharField(max_length=1, null=True, blank=True)
    senddate = models.DateTimeField(null=True, blank=True)
    senddate2 = models.DateTimeField(null=True, blank=True)
    residdate = models.DateTimeField(null=True, blank=True)
    installdate = models.DateTimeField(null=True, blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return self.store.serial

    def pdate(self):
        jd = JDate(self.create.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate)
        return newsdate

    def pdatetime(self):
        jd = JDate(self.create.strftime(_datetemplate))
        newsdate = jd.format('l j E  Y -  H:i')
        return newsdate

    def normal_date(self):
        jd = JDate(self.create.strftime(_datetemplate))
        newsdate = jd.format(_shamsitemplate2)
        return newsdate


def history_post_save(sender, instance, created, *args, **kwargs):
    if created:
        data = instance

        result = StoreHistory.objects.get(pk=data.id)
        try:
            a = 0
            if data.status_id == 6:
                _daghi = data.create
                _start = StoreHistory.objects.filter(store_id=data.store_id, status_id=9, id__lt=data.id).order_by(
                    '-id').first()
                if _start:
                    result.senddate = _start.create
                    if _start.storage_id:
                        if len(str(_start.storage_id)) > 0:
                            a = 1
                            result.storage_id = _start.storage_id
                        if _start.storage.refrence:
                            _start2 = StoreHistory.objects.filter(store_id=data.store_id, status_id=9,
                                                                  id__lt=_start.id).order_by(
                                '-id').first()
                            try:
                                if _start2.storage_id:
                                    if len(str(_start2.storage_id)) > 0:
                                        a = 1
                                        result.storage_id = _start2.storage_id
                                        result.senddate2 = str(_start2.create)
                            except AttributeError:
                                pass

                _start = StoreHistory.objects.filter(store_id=data.store_id, status_id=3, id__lt=data.id).order_by(
                    '-id').first()
                if _start:
                    result.residdate = _start.create
                    if _start.storage_id and a == 0:
                        result.storage_id = _start.storage_id

                _start = StoreHistory.objects.filter(store_id=data.store_id, status_id=5, id__lt=data.id).order_by(
                    '-id').first()
                if _start:
                    _install = _start.create
                    result.installdate = _start.create
                    result.activeday = (result.create - result.installdate).days
                    if result.activeday == 0:
                        result.activeclass = 'A'
                    elif result.activeday == 1:
                        result.activeclass = 'B'
                    elif 1 < result.activeday < 11:
                        result.activeclass = 'C'
                    elif 10 < result.activeday < 21:
                        result.activeclass = 'D'
                    elif 20 < result.activeday < 31:
                        result.activeclass = 'E'
                    else:
                        result.activeclass = 'F'

                if data.starterror:
                    result.activeday = 0
                    result.activeclass = 'A'

                result.save()
                return False

        except ObjectDoesNotExist:
            print('nist')
        except IntegrityError:
            pass
        except TypeError:
            pass


post_save.connect(history_post_save, sender=StoreHistory)


class HistorySt(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)

    def __str__(self):
        return str(self.store.tarikh)


class MozdSanavat(models.Model):
    group = models.PositiveIntegerField(default=7)
    year = models.PositiveIntegerField(default=1402)
    sabeghe = models.PositiveIntegerField(blank=True)
    price = models.PositiveIntegerField()

    def __str__(self):
        return str(self.group) + str(self.sabeghe)


class BaseGroup(models.Model):
    name = models.CharField('شرح', max_length=100)

    class Meta:
        verbose_name = "دسته بندی ارزیابی عملکرد"
        verbose_name_plural = " دسته بندی های ارزیابی عملکرد"

    def __str__(self):
        return self.name


class BaseDetail(models.Model):
    basegroup = models.ForeignKey(BaseGroup, on_delete=models.CASCADE)
    name = models.TextField('شرح')
    d_one = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    d_two = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    class Meta:
        verbose_name = "عنوان ارزیابی عملکرد"
        verbose_name_plural = " عنوان های ارزیابی عملکرد"

    def __str__(self):
        return self.name


class SathKeyffyat(models.Model):
    base_detail = models.ForeignKey(BaseDetail, on_delete=models.CASCADE)
    value_d1 = models.PositiveIntegerField(default=0)
    value_d2 = models.PositiveIntegerField(default=0)
    result = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    period = models.ForeignKey(Mount, on_delete=models.CASCADE)
    uniq = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.zone.name

    @classmethod
    def get_input(cls, value_d1: int, value_d2: int, period: int, zone: int, base_detail_id: int):
        try:
            data = cls.objects.get(period_id=period, zone_id=zone, base_detail_id=base_detail_id)
            data.result = (data.base_detail.d_one * value_d1) + (data.base_detail.d_two * value_d2)
        except cls.DoesNotExist:
            pass


class RepairStoreName(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام کالا')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "معرفی قطعه "
        verbose_name_plural = " معرفی قطعات "


class RepairRole(models.Model):
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='نام تعمیرگاه')
    repairstore = models.ForeignKey(RepairStoreName, on_delete=models.CASCADE, verbose_name='نام قطعه اولیه')
    minvalue = models.PositiveIntegerField(verbose_name='نقطه سفارش')
    startvalue = models.PositiveIntegerField(verbose_name='موجودی اولیه')
    ofroadvalue = models.PositiveIntegerField(default=0, verbose_name='موجودی بین راهی')
    usevalue = models.PositiveIntegerField(blank=True, null=True, verbose_name='درخواست')
    inventory = models.PositiveIntegerField(default=0, verbose_name='رسیده')
    required = models.PositiveIntegerField(default=0, verbose_name='مورد نیاز')
    tedad = models.PositiveIntegerField(default=0, verbose_name='استفاده شده')
    mojodi = models.PositiveIntegerField(default=0)
    uniq = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.storage.name

    def mojodi(self):
        return (int(self.inventory) + int(self.ofroadvalue) + int(self.startvalue)) - int(self.tedad)

    class Meta:
        unique_together = ('storage', 'repairstore')
        verbose_name = "نقطه سفارش قطعه"
        verbose_name_plural = " نقطه سفارش قطعات"


class Repair(models.Model):
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='نام انبار')
    repairstore = models.ForeignKey(RepairStoreName, on_delete=models.CASCADE, verbose_name='نام قطعه')
    store = models.ForeignKey(StoreList, on_delete=models.CASCADE, verbose_name='قطعه', blank=True, null=True)
    valuecount = models.PositiveIntegerField()
    tarikh = jmodels.jDateField(auto_now_add=True, blank=True, null=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    uniq = models.UniqueConstraint(fields=['storage', 'repairstore', 'tarikh', 'store'], name='unique repair')
    status = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.storage.name

    @classmethod
    def checkuserepair(cls, storageid: int):
        required = 0

        for store in RepairRole.objects.filter(storage_id=storageid):
            _startvalue = store.startvalue
            _ofroadvalue = store.ofroadvalue
            _usevalue = store.usevalue
            _tedad = store.tedad
            _inventory2 = store.inventory

            _inventory = store.inventory
            _required = store.required
            repair = Repair.objects.filter(storage_id=storageid, repairstore_id=store.repairstore_id).aggregate(
                tedad=Sum('valuecount'))
            tedad = repair['tedad'] if repair['tedad'] else 0
            if store.tedad > tedad:
                _inventory2 += store.tedad - tedad
            elif tedad > store.tedad:
                _inventory2 -= tedad - store.tedad

            mojodi = (int(_inventory) + int(_ofroadvalue) + int(_startvalue))
            mojodi = mojodi - tedad

            required = int(_usevalue) - mojodi if mojodi <= int(_usevalue) else 0
            # if (mojodi - tedad) > int(_usevalue):
            #     required=0
            # elif mojodi > tedad and tedad < int(_usevalue):
            #     if tedad:
            #         required = (int(_usevalue) - mojodi) + tedad
            #     else:
            #         required = (int(_usevalue) - mojodi)
            #     if required > int(_usevalue):
            #         required = (required) - int(_usevalue)
            # elif mojodi < tedad and tedad< int(_usevalue):
            #     required = tedad - mojodi
            #
            #
            # elif tedad > int(_usevalue):
            #     required = int(_usevalue)
            #
            # elif tedad == mojodi:
            #     required = 0

            # a = tedad - mojodi
            # if tedad < int(_usevalue):
            #     required = int(_usevalue) - abs(a)
            #
            # if abs(a) < int(_usevalue):
            #     required = abs(a)
            # if abs(a) > int(_usevalue):
            #     required = 0

            # if mande >= 0:
            #     required = 0
            # elif mande < 0:
            #     required = int(_usevalue) - abs(mande)
            # elif int(_usevalue) == mande:
            #     required = 0

            # required = _usevalue - mande
            # required = required if required > 0 else 0
            # if store.tedad > tedad:
            #     store.inventory += store.tedad - tedad
            # elif tedad > store.tedad:
            #     store.inventory -= tedad - store.tedad

            store.required = required
            store.tedad = tedad
            store.save()

    class Meta:
        unique_together = ('storage', 'repairstore', 'tarikh', 'store')
        verbose_name = "ثبت قطعه مصرفی"
        verbose_name_plural = " ثبت قطعات مصرفی"


#     def repair_post_save(sender, instance, created, *args, **kwargs):
#         data = instance
#         count_use = Repair.objects.filter(storage_id=data.storage_id).annotate(coun)
#         for item in Role.objects.all():
#             for ref in Refrence.objects.all():
#                 try:
#                     uniq = str(ref.id) + '-' + str(item.id) + '-' + str(data.id)
#                     DefaultPermission.objects.create(role_id=item.id,
#                                                      semat_id=ref.id,
#                                                      accessrole_id=5,
#                                                      permission_id=int(data.id),
#                                                      unid=uniq)
#                 except IntegrityError:
#                     continue
#
# post_save.connect(repair_post_save, sender=Repair)


class RepairStore(models.Model):
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='نام انبار')
    repairstore = models.ForeignKey(RepairStoreName, on_delete=models.CASCADE, verbose_name='نام قطعه')
    req = models.PositiveIntegerField()
    tarikh = jmodels.jDateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(StatusRef, on_delete=models.CASCADE, verbose_name='وضعیت')

    def __str__(self):
        return self.storage.name

    class Meta:
        verbose_name = "سفارش قطعه"
        verbose_name_plural = " سفارش قطعات"


class Tadiltemp(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    period = models.PositiveIntegerField(blank=True, null=True)
    khordad = models.PositiveIntegerField(default=0)
    khordad_olad = models.PositiveIntegerField(default=0)
    khordad_ezafe = models.PositiveIntegerField(default=0)
    khordad_jazb = models.PositiveIntegerField(default=0)
    khordad_etlaf = models.PositiveIntegerField(default=0)
    tir = models.PositiveIntegerField(default=0)
    tir_olad = models.PositiveIntegerField(default=0)
    tir_ezafe = models.PositiveIntegerField(default=0)
    tir_jazb = models.PositiveIntegerField(default=0)
    tir_etlaf = models.PositiveIntegerField(default=0)
    mordad = models.PositiveIntegerField(default=0)
    mordad_olad = models.PositiveIntegerField(default=0)
    mordad_ezafe = models.PositiveIntegerField(default=0)
    mordad_jazb = models.PositiveIntegerField(default=0)
    mordad_etlaf = models.PositiveIntegerField(default=0)
    shahrivar = models.PositiveIntegerField(default=0)
    shahrivar_olad = models.PositiveIntegerField(default=0)
    shahrivar_ezafe = models.PositiveIntegerField(default=0)
    shahrivar_jazb = models.PositiveIntegerField(default=0)
    shahrivar_etlaf = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.owner.get_full_name()


class StoreView(models.Model):
    store = models.ForeignKey(StoreList, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, blank=True, null=True)
    serial = models.CharField(max_length=15)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    send_date = models.DateTimeField(null=True, blank=True)
    resid_date = models.DateTimeField(null=True, blank=True)
    tek_date = models.DateTimeField(null=True, blank=True)
    gs_date = models.DateTimeField(null=True, blank=True)
    fail_date = models.DateTimeField(null=True, blank=True)
    starterr = models.BooleanField()
    status = models.PositiveIntegerField()

    def __str__(self):
        return str(self.serial)


class ImgSerial(models.Model):
    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        ext = "jpg"
        filename = f"{unique_id}.{ext}"
        return os.path.join("store/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 500
        if filesize > megabyte_limit * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    store = models.ForeignKey(StoreList, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to=wrapper)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    imageid = models.CharField(max_length=50, default=0, validators=[validate_image])

    def __str__(self):
        return str(self.store.serial)

    def save(self, *args, **kwargs):
        if self.img:
            super().save(*args, **kwargs)
            img = Image.open(self.img.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.img.path)


class InsertPayroll(models.Model):
    actions = models.CharField(max_length=2, choices=[('1', 'برای همه اعمال گردد'), ('2', ' برای یک گروه اعمال گردد'),
                                                      ('3', ' به یک نفر اعمال گردد')], verbose_name='مدل', null=True,
                               blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True, verbose_name='انتخاب شخص')
    baseparametr = models.ForeignKey(PayBaseParametrs, on_delete=models.CASCADE, null=True, blank=True,
                                     verbose_name='آیتم حقوقی')
    group = models.PositiveIntegerField(default=0, verbose_name='انتخاب گروه')
    start_date = models.ForeignKey(Mount, on_delete=models.CASCADE, null=True, blank=True, verbose_name='تاریخ آغاز')
    end_date = models.CharField(max_length=2, choices=[('1', 'از این به بعد'), ('2', ' فقط همین ماه'),
                                                       ], null=True, blank=True,
                                verbose_name='تاریخ پایان')
    darsad = models.PositiveIntegerField(default=0, verbose_name='درصد ')
    action = models.CharField(max_length=2, choices=[('1', 'بدون فرمول'), ('2', 'فرمول محاسباتی دارد')],
                              verbose_name='نوع فرمول')
    formol = models.CharField(max_length=500, null=True, blank=True, verbose_name='فرمول',
                              help_text='paye=دستمزد روزانه بدون سنوات, pays=دستمزد روزانه با سنوات , days=تعداد روز ماه')
    mablagh = models.PositiveIntegerField(default=0, verbose_name='مبلغ')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.baseparametr)


def insertpayroll_post_save(sender, instance, created, *args, **kwargs):
    data = instance
    if data.actions == '1':
        owners = Owner.objects.filter(active=True, role__role='tek')
    if data.actions == '2':
        owners = Owner.objects.filter(active=True, role__role='tek', job_group=data.group)
    if data.actions == '3':
        owners = Owner.objects.filter(active=True, id=data.owner.id)
    for owner in owners:
        old_in_payment = PersonPayment.objects.filter(owner_id=owner.id, baseparametr_id=data.baseparametr.id).order_by(
            '-id')
        if old_in_payment:
            old_price = old_in_payment[0].price
        else:
            old_price = data.baseparametr.price
        if data.darsad > 0:
            _price = ((old_price * data.darsad) / 100) + old_price
        elif data.mablagh > 0:
            _price = (data.mablagh) + old_price
        if data.mablagh == 0 and data.darsad == 0:
            _price = old_price
        uniq = str(owner.id) + "-" + str(data.baseparametr.id) + "-" + str(
            data.start_date)
        try:

            maxmount = Payroll.objects.filter(tek_id=owner.id).aggregate(maxdate=Max('period_id'))

            if maxmount['maxdate']:
                mounts = Mount.objects.filter(id__gte=data.start_date.id, id__lte=maxmount['maxdate'])
                a = ''
                if mounts is not None:
                    for mount in mounts:
                        a += str(mount.id) + "#"
            else:
                a = 0

            PersonPayment.objects.create(owner_id=owner.id, insertpyroll_id=data.id,
                                         baseparametr_id=data.baseparametr.id, price=_price,
                                         start_date=data.start_date, end_date=data.end_date, darsad=data.darsad,
                                         mablagh=data.mablagh, uniqid=uniq, tadil=a)
        except IntegrityError:
            continue


post_save.connect(insertpayroll_post_save, sender=InsertPayroll)


class PersonPayment(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    insertpyroll = models.ForeignKey(InsertPayroll, on_delete=models.CASCADE, null=True, blank=True)
    baseparametr = models.ForeignKey(PayBaseParametrs, on_delete=models.CASCADE)
    start_date = models.ForeignKey(Mount, on_delete=models.CASCADE, null=True, blank=True, verbose_name='تاریخ آغاز')
    end_date = models.CharField(max_length=2, choices=[('1', 'از این به بعد'), ('2', ' فقط همین ماه'),
                                                       ], null=True, blank=True,
                                verbose_name='تاریخ پایان')
    darsad = models.PositiveIntegerField(default=0, verbose_name='درصد ')
    mablagh = models.PositiveIntegerField(default=0, verbose_name='مبلغ')
    price = models.PositiveIntegerField(default=0, verbose_name='مبلغ دریافتی')
    tadil = models.CharField(max_length=200, null=True, blank=True, verbose_name='تاریخ های اعمال تعدیل')
    uniqid = models.CharField(max_length=25, unique=True, blank=True, null=True)

    def __str__(self):
        return str(self.owner)


class ZoneToStorage(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.zone.name)


class kargahToStorage(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.zone.name)


class StoreManufacturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SerialRange(models.Model):
    storemanufacturer = models.ForeignKey(StoreManufacturer, on_delete=models.CASCADE)
    serialnumber = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.serialnumber


class GenerateSerialNumber(models.Model):
    name = models.CharField(max_length=100)
    partnumber = models.CharField(max_length=3, unique=True)
    serialnumber = models.PositiveIntegerField()
    status = models.ForeignKey(StatusStore, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
