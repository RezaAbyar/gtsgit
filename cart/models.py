import datetime
import jdatetime
from django.db import models
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
from base.models import GsModel, Area, Product, Owner
from jalali.Jalalian import JDate
from django.conf import settings
from base.modelmanager import RoleeManager
import jalali

class phoneverify(models.Model):
    phone = models.CharField(max_length=11)
    code = models.IntegerField()

    def __str__(self):
        return self.phone


class StatusPan(models.Model):
    info = models.CharField(max_length=100)

    def __str__(self):
        return self.info






class PanModels(models.Model):
    pan = models.CharField(max_length=16)
    vin = models.CharField(max_length=17, blank=True, db_index=True)
    create = jmodels.jDateField(auto_now=True)
    update = jmodels.jDateField(auto_now_add=True)
    time = models.TimeField(auto_now=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statuspan = models.ForeignKey(StatusPan, on_delete=models.CASCADE)
    tarikhShamsi = models.CharField(max_length=20, null=True,blank=True)
    tarikh = jmodels.jDateField(blank=True,null=True)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE, null=True,blank=True)
    nahye = models.ForeignKey(Area, on_delete=models.CASCADE,null=True, blank=True)
    uniq = models.CharField(unique=True, max_length=100, blank=True)
    tarikhnahye = models.CharField(max_length=20, blank=True,null=True)
    tarikhmalek = models.CharField(max_length=20, blank=True,null=True)
    tarikhsetad = models.CharField(max_length=20, blank=True,null=True)
    tarikhemha = models.CharField(max_length=20, blank=True,null=True)
    tarikhchangetarashe = models.CharField(max_length=20, blank=True,null=True)
    FirstCode = models.CharField(max_length=2, blank=True,null=True)
    SecondCode = models.CharField(max_length=3, blank=True,null=True)
    CityCode = models.CharField(max_length=2, blank=True,null=True)
    CharCode = models.CharField(max_length=3, blank=True,null=True)
    FirstCode_MS = models.CharField(max_length=3, blank=True,null=True)
    SecondCode_MS = models.CharField(max_length=5, blank=True,null=True)
    status = models.PositiveIntegerField(blank=True,null=True)
    malek = models.CharField(max_length=50, blank=True,null=True)
    codemelimalek = models.CharField(max_length=10, blank=True,null=True)
    showcardmeli = models.BooleanField(default=False)
    showcardcar = models.BooleanField(default=False)
    mobailmalek = models.CharField(max_length=11, blank=True,null=True)
    expire_date_area=models.PositiveBigIntegerField()
    oldpan = models.CharField(max_length=16, null=True, blank=True)
    infochange = models.CharField(max_length=200, null=True, blank=True)

    object_role = RoleeManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.pan)


    def expire_date(self):
        counter=0
        expire_day = 0
        today = jdatetime.date.today()
        create = self.tarikh
        send_date = create + datetime.timedelta(days=settings.TIME_CARD_IN_GS)
        if settings.ALLOWED_CARDS_IN_DAHE == True:
            day = send_date.day
            day -= 1
            if day < 11:
                counter = 10 - int(day)
            if day > 10 and day < 21:
                counter = 20 - int(day)
            if day > 20:
                counter = 31 - int(day)
            counter -= 1
            send_date = send_date + datetime.timedelta(days=counter)

            expire_day = (today - send_date).days

        if settings.ALLOWED_CARDS_IN_DAHE == False:
            expire_day = (today - send_date).days

        return expire_day

    def expire_date_area(self):
        expire_day_area = 0
        if self.tarikhnahye:
            mdate = self.tarikhnahye.split("-")

            create =jdatetime.date(int(mdate[0]),int(mdate[1]),int(mdate[2]))
            # createnow= jdatetime.date(create.year,create.month,create.day)

            send_date = create + datetime.timedelta(days=settings.TIME_CARD_IN_AREA)


            today = jdatetime.date.today()
            expire_day_area = (today - send_date).days

            return expire_day_area
        return 0


class ValidPan(models.Model):
    pan = models.PositiveBigIntegerField(db_index=True)
    vin = models.CharField(max_length=28)

    def __str__(self):
        return str(self.pan)


class PanHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pan = models.ForeignKey(PanModels, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusPan, on_delete=models.CASCADE)
    detail = models.TextField()
    create = models.DateTimeField(auto_now_add=True, blank=True)
    persiandate = models.DateTimeField(blank=True)

    def __int__(self):
        return self.pan.pan

    def persiandate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('l j E  Y   H:i')
        return newsdate


class StatusCardAzad(models.Model):
    create = models.DateTimeField(auto_now_add=True)
    name = models.CharField('شرح', max_length=40)

    class Meta:
        verbose_name = "پارامتر کارت آزاد"
        verbose_name_plural = " پارامتر های کارت آزاد"

    def __str__(self):
        return self.name


class CardAzad(models.Model):
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    pan = models.CharField(max_length=18, unique=True)
    vin = models.CharField(max_length=19)
    gs = models.ForeignKey(GsModel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusCardAzad, on_delete=models.CASCADE)
    cardst = models.PositiveIntegerField(default=1)
    date_transition = models.CharField(max_length=12, blank=True)

    class Meta:
        verbose_name = "لیست کارت آزاد"
        verbose_name_plural = " لیست کارت های آزاد"
        ordering = (
            "gs__area",
            "gs_id",
            "status",

        )

    def __str__(self):
        return str(self.pan)


class CardHistory(models.Model):
    card_id = models.ForeignKey(CardAzad, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(StatusCardAzad, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.card_id.pan)

    def persiandate(self):
        jd = JDate(self.create.strftime("%Y-%m-%d %H:%M:%S"))
        newsdate = jd.format('l j E  Y   H:i')
        return newsdate


class CardLog(models.Model):
    card_id = models.CharField(max_length=20)
    create = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=20)
    status = models.BooleanField()

    def __str__(self):
        return str(self.card_id)