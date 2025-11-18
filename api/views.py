import sys
import shutil
import logging
from django.db import transaction
import redis
from django.conf import settings
from datetime import datetime, date
from operator import itemgetter
from django.db.models import F, Avg, Count, Sum, Case, When, Max
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from jalali.Jalalian import JDate
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from accounts.logger import add_to_log
from accounts.models import Captcha
from base.models import Area, GsModel, Pump, Ticket, Zone, FailureSub, Owner, Operator, Modem, Rack, Ipc, Status, \
    Statuspump, PumpBrand, Product, GsList, CloseGS, Parametrs, DefaultPermission, UserPermission, WorkflowLog, \
    GsStatus, Workflow, Reply, OwnerFiles, OwnerChild, City, Printer, ThinClient, Refrence, Peykarbandylog
from lock.models import LockModel, InsertLock, SendPoshtiban, Position, LockLogs
from msg.models import CreateMsg, ListMsg
from pay.models import SathKeyffyat, BaseDetail, Store, StoreList, StoreHistory, StatusRef, GenerateSerialNumber, \
    ImgSerial
from cart.models import PanModels, PanHistory
from sell.models import SellModel, IpcLog, SellGs, InfoEkhtelafLogs, EditSell, AcceptForBuy, OpenCloseSell, \
    CloseSellReport, IpcLogHistory, Waybill, SellTime
from rest_framework.permissions import IsAuthenticated
import jdatetime
from sell.models import SellModel, Mojodi, AccessChangeSell, ModemDisconnect
from utils.exception_helper import to_miladi
from visit.models import CBrand
from .serializers import AreaSerializer, GSSerializer, OwnerSerializer, CaptchaSerializer, SellSerializer, \
    FailureSerializer, WaybillSerializer
from permission import GSCreatePermission
from rest_framework.views import APIView
import random
from django.db import IntegrityError
from .init import CoreAPIView, BaseAPIView
from .utils import string_assets
from .utils.exception_helper import BadRequest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import datetime
from django.db.models import Q
from pay.models import Repair
from base.views import SendOTP2, createotp, zoneorarea
from cart.views import checknumber
from base.code import generateotp
import json
import re

today_date = str(datetime.date.today())
startdate = today_date[:8]
startdate = startdate + "01"


def validate_advanced_location(location):
    """
    اعتبارسنجی پیشرفته برای فرمت لوکیشن
    """
    # حذف فاصله‌های اضافی
    location = location.strip()

    # بررسی وجود کاما
    if ',' not in location:
        return False, "فرمت نامعتبر. باید از کاما برای جدا کردن lat و long استفاده کنید"

    parts = location.split(',')
    if len(parts) != 2:
        return False, "فرمت نامعتبر. فقط یک کاما مجاز است"

    lat, long = parts[0].strip(), parts[1].strip()

    # بررسی الگوی هر بخش
    lat_pattern = r'^-?\d{1,3}\.\d{5,}$'
    long_pattern = r'^-?\d{1,3}\.\d{5,}$'

    if not re.match(lat_pattern, lat):
        return False, "فرمت عرض جغرافیایی (lat) نامعتبر. مثال صحیح: 36.520867"

    if not re.match(long_pattern, long):
        return False, "فرمت طول جغرافیایی (long) نامعتبر. مثال صحیح: 53.077987"

    # تبدیل به عدد و بررسی محدوده
    try:
        lat_float = float(lat)
        long_float = float(long)

        if not (-90 <= lat_float <= 90):
            return False, "عرض جغرافیایی باید بین -90 تا 90 باشد"

        if not (-180 <= long_float <= 180):
            return False, "طول جغرافیایی باید بین -180 تا 180 باشد"

        # بررسی دقیق‌تر برای ایران (اختیاری)
        if 25 <= lat_float <= 40 and 44 <= long_float <= 64:
            # مختصات در محدوده ایران است
            pass
        else:
            # می‌توانید هشدار بدهید یا رد کنید
            pass

    except ValueError:
        return False, "مقادیر عددی نامعتبر"

    return True, "فرمت صحیح است"


class CaptchaView(APIView):

    def get(self, request):
        r1 = random.randint(1, 61)
        _list = Captcha.objects.get(id=r1)
        srz_data = CaptchaSerializer(instance=_list)
        return JsonResponse({'mylist': srz_data.data})


def validate_serial_format(serial):
    """
    Validate that serial has exactly 2 English letters at the beginning and the rest are digits
    Example valid formats: AB1234, XY98765
    """
    if len(serial) < 5 or len(serial) > 9:
        return False

    # Check first two characters are English letters (upper or lower case)
    # Check if format is two letters followed by digits
    if len(serial) >= 5:
        first_tree = serial[:3]
        if first_tree.isalpha():
            return False
        first_two = serial[:2]
        if (first_two.isalpha() and all(ord(c) < 128 for c in first_two)
                and serial[2:].isdigit()):
            return True

        # Check if format is one letter followed by digits
        first_char = serial[0]
        if (first_char.isalpha() and ord(first_char) < 128
                and serial[1:].isdigit()):
            return True

    return False


class GsTicketView(APIView):

    def get(self, request):
        mylist = []
        data = request.GET.get('gsid')
        _id = int(data)
        _list = Ticket.objects.filter(gs_id=_id).aggregate(master=Count(Case(When(failure_id=1045, then=1))),
                                                           pinpad=Count(Case(When(reply_id__in=[3, 4], then=1))))
        _listfailure = Ticket.objects.values('failure_id', 'failure__info').filter(gs_id=_id).annotate(
            tedad=Count('id'))
        for item in _listfailure:
            dict = {
                'info': item['failure__info'],
                'tedad': item['tedad']
            }
            mylist.append(dict)
        _listfake = Ticket.objects.filter(gs_id=_id, reply_id__in=[50, 54]).aggregate(tedad=Count('id'))
        dict = {
            'info': 'تیکت فیک',
            'tedad': _listfake['tedad']
        }
        mylist.append(dict)
        mylist = sorted(mylist, key=itemgetter('tedad'), reverse=False)

        return JsonResponse({'list': _list, 'mylist': mylist})


class CreateGs(viewsets.ViewSet):
    thislist = []
    permission_classes = [IsAuthenticated, GSCreatePermission]

    def create(self, request):

        serializer = GSSerializer
        self.check_object_permissions(request, serializer)
        if self.request.method == "POST":

            user = self.request.user.id
            gsid = request.data.get('gsid')
            name = request.data.get('name')
            address = request.data.get('address')
            phone = request.data.get('phone')
            area = request.data.get('area')
            data = {'user': user, 'gsid': gsid, 'name': name, 'address': address, 'phone': phone, 'area': area}
            serializer = serializer(data=data)

            if serializer.is_valid():
                return Response({'msg': 'Data  created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateOwner(viewsets.ViewSet):
    thislist = []

    def create(self, request):
        serializer = OwnerSerializer
        if self.request.method == "POST":

            name = request.data.get('name')
            lname = request.data.get('lname')
            codemeli = request.data.get('codemeli')
            mobail = request.data.get('mobail')
            zone = request.data.get('zone')
            area = request.data.get('area')
            role = request.data.get('role')
            password1 = request.data.get('Password1')
            if zone == '0':
                zone = ''

            if area == '0':
                area = ''

            user = User.objects.create_user(codemeli, 'aa@tt.com')
            user.set_password(password1)
            user.last_name = lname
            user.first_name = name
            user.save()
            data = {'user': user.id, 'name': name, 'lname': lname, 'mobail': mobail, 'codemeli': codemeli,
                    'zone': zone, 'area': area, 'role': role}
            serializer = serializer(data=data)

            if serializer.is_valid():
                instance = serializer.save()

                return JsonResponse({"message": 'success', 'mylist': instance})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddNazel(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    @transaction.atomic
    def create(self, request):

        serializer = SellSerializer
        # self.check_object_permissions(request, serializer)
        if self.request.method == "POST":
            benzin = str(request.POST.get('benzin_mojodi'))
            _super = str(request.POST.get('super_mojodi'))
            gaz = str(request.POST.get('gaz_mojodi'))
            datein = str(request.POST.get('tarikh'))
            datein = datein.split("/")
            tarikh = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            end = request.POST.get('end')
            end2 = request.POST.get('end2')
            start = request.POST.get('start')
            start2 = request.POST.get('start2')
            sell = request.POST.get('sellshow')
            number = request.POST.get('number')
            gs = request.POST.get('gsid')
            sellkol_h = request.POST.get('sellkol')
            id_ekhtelaf = request.POST.get('id_ekhtelaf')
            yarane = request.POST.get('yarane')
            azad = request.POST.get('azad')
            ezterari = request.POST.get('ezterari')
            mojaz = request.POST.get('mojaz')
            nomojaz = request.POST.get('nomojaz')
            haveleh = request.POST.get('havale')
            azmayesh = request.POST.get('azmayesh')
            pumpnumber = Pump.objects.get(id=int(number))

            ac = AccessChangeSell.objects.filter(gs_id=int(pumpnumber.gs.id), pump_id=int(pumpnumber.id), tarikh=tarikh,
                                                 active=True,
                                                 editor_id=request.user.owner.id).count()
            if ac > 0:
                isedit = 1
            else:
                isedit = 0
            # benzin = 0 if len(benzin) < 1 else benzin
            # _super = 0 if len(_super) < 1 else _super
            # gaz = 0 if len(gaz) < 1 else gaz
            # _mojodi = True
            # try:
            #     ipclog = IpcLog.objects.get(gs_id=gs)
            #     if ipclog.dashboard_version != '1.03.052001':
            #         _mojodi = False
            # except ObjectDoesNotExist:
            #     _mojodi = True
            # if _mojodi:
            #     Mojodi.objects.filter(gs_id=gs, tarikh=tarikh).delete()
            #     Mojodi.objects.create(gs_id=gs, tarikh=tarikh, benzin=benzin, super=_super, gaz=gaz,
            #                           uniq=str(gs) + '-' + str(tarikh))

            sellold2 = SellModel.objects.filter(tolombeinfo_id=number, tarikh__lt=tarikh).order_by('-tarikh').first()
            try:
                _sellold = False
                sellold = SellModel.objects.filter(gs_id=gs, tolombeinfo_id=number).order_by('-tarikh')[10:].first()

                if SellModel.objects.filter(gs_id=gs, tolombeinfo_id=number).count() > 9:
                    _sellold = True

                sells = SellModel.objects.get(uniq=str(tarikh) + "-" + str(gs) + "-" + str(number))

                if sells.gs.isqrcode or isedit == 1:
                    if str(sells.ezterari) != ezterari:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.ezterari,
                                                new=ezterari, status='آزاد جایگاه')

                    if str(sells.yarane) != yarane:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.yarane,
                                                new=yarane, status='یارانه')
                    if str(sells.azad) != azad:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.azad,
                                                new=azad, status='آزاد')
                    if str(sells.haveleh) != haveleh:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.haveleh,
                                                new=haveleh, status='حواله')
                    if str(sells.azmayesh) != azmayesh:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.azmayesh,
                                                new=azmayesh, status='آزمایش')

                    if sells.end and str(sells.end) != end and int(sells.end) > 0:
                        EditSell.objects.create(owner_id=request.user.owner.id, sell_id=sells.id, old=sells.end,
                                                new=end, status='شمارنده اول وقت')

                    sells.ezterari = ezterari
                    sells.yarane = yarane
                    sells.azad = azad
                    sells.sellkol = sellkol_h
                    sells.haveleh = haveleh
                    sells.azmayesh = azmayesh
                    sells.start = int(start)
                    sells.t_start = int(start2)
                    sells.end = int(end)
                    sells.t_end = int(end2)
                    sells.sell = int(sell)

                if sellold2 and int(end) != sellold2.start:
                    sells.mogh = 1
                    sells.moghnumber = sellold2.start
                else:
                    sells.mogh = 0
                    sells.moghnumber = 0

                if sellold and _sellold:
                    if sells.tarikh > sellold.tarikh or sells.gs.isqrcode:
                        sells.start = int(start)
                        sells.t_start = int(start2)
                        sells.end = int(end)
                        sells.t_end = int(end2)
                        sells.sell = int(sell)
                if _sellold == False:
                    sells.start = int(start)
                    sells.t_start = int(start2)
                    sells.end = int(end)
                    sells.t_end = int(end2)
                    sells.sell = int(sell)

                sells.start = int(start)
                sells.t_start = int(start2)
                sells.end = int(end)
                sells.t_end = int(end2)
                sells.sell = int(sell)
                sells.ekhtelaf = id_ekhtelaf
                sells.mojaz = mojaz
                sells.nomojaz = nomojaz
                sells.nomojaz2 = nomojaz
                sells.save()
                SellGs.sell_get_or_create(gs=sells.gs_id, tarikh=sells.tarikh)

            except SellModel.DoesNotExist:
                if sellold2 and int(end) != sellold2.start:
                    _mogh = 1
                    _moghnumber = sellold2.start
                else:
                    _mogh = 0
                    _moghnumber = 0
                SellModel.objects.create(gs_id=gs, tolombeinfo_id=number, start=start, end=end, sell=sell,
                                         ezterari=ezterari, pumpnumber=pumpnumber.number,
                                         product_id=pumpnumber.product_id, mogh=_mogh, moghnumber=_moghnumber,
                                         tarikh=tarikh, yarane=yarane, azad=azad, sellkol=sellkol_h,
                                         haveleh=haveleh, azmayesh=azmayesh,
                                         uniq=str(tarikh) + "-" + str(gs) + "-" + str(number))
                SellGs.sell_get_or_create(gs=gs, tarikh=tarikh)
            _list = SellModel.objects.filter(tarikh=tarikh, gs_id=gs).order_by('-tolombeinfo_id')
            srz_data = SellSerializer(instance=_list, many=True)
            _sum = SellModel.objects.filter(tarikh=tarikh, gs_id=gs).aggregate(summek=Sum('sell'),
                                                                               sumelk=Sum('sellkol'))

            sumlist = []

            if _sum['summek']:
                summek = _sum['summek']
            else:
                summek = 0
            if _sum['sumelk']:
                sumelk = _sum['sumelk']
            else:
                sumelk = 0

            _dict = {
                'summek': summek,
                'sumelk': sumelk,
            }

            sumlist.append(_dict)
            return JsonResponse({"message": 'success', 'mylist': srz_data.data, 'sumlist': sumlist})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddNazel2(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    @transaction.atomic
    def create(self, request):
        serializer = SellSerializer
        # self.check_object_permissions(request, serializer)
        if self.request.method == "POST":

            datein = str(request.POST.get('tarikh'))
            dateout = str(request.POST.get('tarikh2'))
            crashdate = str(request.POST.get('tarikh3'))
            # crashmodel = int(request.POST.get('crashmodel'))
            az = datein
            ta = dateout
            datein = datein.split("/")
            dateout = dateout.split("/")
            crashdate = crashdate.split("/")
            tarikh = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            tarikh2 = jdatetime.date(day=int(dateout[2]), month=int(dateout[1]), year=int(dateout[0])).togregorian()
            crashdate = jdatetime.date(day=int(crashdate[2]), month=int(crashdate[1]),
                                       year=int(crashdate[0])).togregorian()
            # if crashmodel == 1:
            #     crashdate = tarikh2 - datetime.timedelta(days=1)
            # else:
            #     crashdate = crashdate

            end = request.POST.get('end')
            end2 = request.POST.get('end2')
            start = request.POST.get('start')
            start2 = request.POST.get('start2')
            sell = request.POST.get('sellshow')
            number = request.POST.get('number')
            gs = request.POST.get('gsid')
            sellkol_h = request.POST.get('sellkol')
            id_ekhtelaf = request.POST.get('id_ekhtelaf')
            yarane = request.POST.get('yarane')

            azad = request.POST.get('azad')
            ezterari = request.POST.get('ezterari')
            mojaz = request.POST.get('mojaz')
            nomojaz = request.POST.get('nomojaz')
            haveleh = request.POST.get('havale')
            azmayesh = request.POST.get('azmayesh')
            information = request.POST.get('information')
            pumpnumber = Pump.objects.get(id=int(number))
            expire_sell = SellModel.objects.exclude(tarikh=crashdate).filter(tarikh__gt=tarikh, tarikh__lt=tarikh2,
                                                                             gs_id=gs).values('tarikh').count()
            if expire_sell > 0:
                return JsonResponse(
                    {"message": 'ابتدا فروش های ما بین دوره های انتخابی را حذف کنید', 'mylist': "0", 'sumlist': "0"})

            try:
                sells = SellModel.objects.get(uniq=str(crashdate) + "-" + str(gs) + "-" + str(number))
                sells.start = int(start)
                sells.end = int(end)
                sells.t_start = int(start2) if start2 is not None else 0
                sells.t_end = int(end2) if end2 is not None else 0
                sells.sell = int(sell)
                sells.yarane = yarane
                sells.azad = azad
                sells.ezterari = ezterari
                sells.haveleh = haveleh
                sells.azmayesh = azmayesh
                sells.umpnumber = pumpnumber
                sells.sellkol = sellkol_h
                sells.ekhtelaf = id_ekhtelaf
                sells.mojaz = mojaz
                sells.nomojaz = nomojaz
                sells.nomojaz2 = nomojaz
                sells.product_id = pumpnumber.product_id
                sells.haveleh = haveleh
                sells.azmayesh = azmayesh
                sells.information = information
                sells.iscrash = True
                sells.save()
                SellGs.sell_get_or_create(gs=gs, tarikh=crashdate)

            except SellModel.DoesNotExist:
                SellModel.objects.create(gs_id=gs, tolombeinfo_id=number, start=start, end=end, sell=sell,
                                         ezterari=ezterari, pumpnumber=pumpnumber.number,
                                         tarikh=crashdate, yarane=yarane, azad=azad, sellkol=sellkol_h,
                                         haveleh=haveleh, azmayesh=azmayesh, mojaz=mojaz, nomojaz=nomojaz,
                                         nomojaz2=nomojaz,
                                         ekhtelaf=id_ekhtelaf, dore=str(az) + "-" + str(ta), iscrash=True,
                                         information=information, product_id=pumpnumber.product_id,
                                         uniq=str(crashdate) + "-" + str(gs) + "-" + str(number))
                SellGs.sell_get_or_create(gs=gs, tarikh=crashdate)

            _list = SellModel.objects.filter(tarikh=crashdate, gs_id=gs).order_by('-tolombeinfo_id')
            srz_data = SellSerializer(instance=_list, many=True)
            _sum = SellModel.objects.filter(tarikh=crashdate, gs_id=gs).aggregate(summek=Sum('sell'),
                                                                                  sumelk=Sum('sellkol'))
            sumlist = []

            if _sum['summek']:
                summek = _sum['summek']
            else:
                summek = 0
            if _sum['sumelk']:
                sumelk = _sum['sumelk']
            else:
                sumelk = 0

            _dict = {
                'summek': summek,
                'sumelk': sumelk,
            }

            sumlist.append(_dict)
            return JsonResponse({"message": 'success', 'mylist': srz_data.data, 'sumlist': sumlist})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowDateSell(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        serializer = SellSerializer

        if self.request.method == "POST":
            datein = str(request.POST.get('tarikh'))
            datein = datein.split("/")
            tarikh = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            gs = request.POST.get('gsid')
            _list = SellModel.objects.filter(tarikh=tarikh, gs_id=gs).order_by('-tolombeinfo__number')
            srz_data = SellSerializer(instance=_list, many=True)
            _sum = SellModel.objects.filter(tarikh=tarikh, gs_id=gs).aggregate(summek=Sum('sell'),
                                                                               sumelk=Sum('sellkol'))
            sumlist = []

            if _sum['summek']:
                summek = _sum['summek']
            else:
                summek = 0
            if _sum['sumelk']:
                sumelk = _sum['sumelk']
            else:
                sumelk = 0

            _dict = {
                'summek': summek,
                'sumelk': sumelk,
            }

            sumlist.append(_dict)

            return JsonResponse({"message": 'success', 'mylist': srz_data.data, 'sumlist': sumlist})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowDateSell2(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        serializer = SellSerializer

        if self.request.method == "POST":
            datein = str(request.POST.get('tarikh'))
            dateout = str(request.POST.get('tarikh2'))
            crashdate = str(request.POST.get('tarikh3'))
            # crashmodel = int(request.POST.get('crashmodel'))
            datein = datein.split("/")
            dateout = dateout.split("/")
            crashdate = crashdate.split("/")
            tarikh = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            tarikh2 = jdatetime.date(day=int(dateout[2]), month=int(dateout[1]), year=int(dateout[0])).togregorian()
            crashdate = jdatetime.date(day=int(crashdate[2]), month=int(crashdate[1]),
                                       year=int(crashdate[0])).togregorian()

            # if crashmodel == 1:
            # crashdate = tarikh2 - datetime.timedelta(days=1)
            # else:
            #     crashdate = tarikh2
            gs = request.POST.get('gsid')
            SellModel.objects.exclude(tarikh=crashdate).filter(gs_id=gs, product_id__isnull=True).delete()
            _list = SellModel.objects.filter(tarikh=crashdate, gs_id=gs).order_by('-tolombeinfo__number')
            srz_data = SellSerializer(instance=_list, many=True)
            _sum = SellModel.objects.filter(tarikh=crashdate, gs_id=gs).aggregate(summek=Sum('sell'),
                                                                                  sumelk=Sum('sellkol'))

            expire_sell = SellModel.objects.exclude(tarikh=crashdate).filter(tarikh__gt=tarikh, tarikh__lt=tarikh2,
                                                                             gs_id=gs).values('tarikh').annotate(
                co=Count(id))
            _expire = []
            for ex in expire_sell:
                # if ex.product_id
                dict = {
                    'ex': str(ex['tarikh'])
                }
                _expire.append(dict)

            sumlist = []

            if _sum['summek']:
                summek = _sum['summek']
            else:
                summek = 0
            if _sum['sumelk']:
                sumelk = _sum['sumelk']
            else:
                sumelk = 0

            _dict = {
                'summek': summek,
                'sumelk': sumelk,
            }

            sumlist.append(_dict)

            return JsonResponse({"message": 'success', 'mylist': srz_data.data, 'sumlist': sumlist, 'expire': _expire})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetSellInfo(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        parametr = Parametrs.objects.all().first()
        data = self.get_data(request.GET)
        status = 1
        select = data['period'].split("-")
        select = jdatetime.date(day=int(select[2]), month=int(select[1]),
                                year=int(select[0])).togregorian()
        gsok = GsModel.objects.get(gsid=data['gsid'])
        if gsok.area.zone.bypass_sell:
            gsis = data['gsid']
            nerkh_yarane = 0
            nerkh_azad = 0
            nerkh_ezterari = 0
            nerkh_azmayesh = 0
            nerkh_havaleh = 0

            return JsonResponse(
                {'gsid': gsis, 'date': data['period'], 'nerkh_yarane': nerkh_yarane,
                 'nerkh_azad': nerkh_azad,
                 'status': 1,
                 'nerkh_ezterari': nerkh_ezterari,
                 'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})
        SellModel.objects.filter(gs__gsid=data['gsid'], product_id__isnull=True).delete()
        try:
            _sellcount = SellModel.objects.filter(gs__gsid=data['gsid'], tarikh=data['period'], islocked=False).count()
            if _sellcount > 0:
                return JsonResponse({'status': 8})

            if gsok.issell == False:
                return JsonResponse({'status': 2})

            # gsok = gsok.gsid



        except GsModel.DoesNotExist:
            return JsonResponse({'status': 2})

        tarikh = data['period']

        try:

            if data['period']:
                sellcount = SellModel.objects.filter(gs__gsid=data['gsid'], tarikh=data['period']).count()
                if sellcount == 0:

                    try:
                        _date = []
                        end_date = CloseGS.objects.filter(gs__gsid=data['gsid'],
                                                          ).order_by('-id')

                        for item in end_date:

                            if select >= item.date_in and select <= item.date_out:
                                gsis = data['gsid']
                                nerkh_yarane = 0
                                nerkh_azad = 0
                                nerkh_ezterari = 0
                                nerkh_azmayesh = 0
                                nerkh_havaleh = 0
                                _owner = item.owner_id if item.owner_id else ''
                                CloseSellReport.objects.create(gs_id=item.gs_id, tarikh=select, owner_id=_owner,
                                                               status=item.status)
                                return JsonResponse(
                                    {'gsid': gsis, 'date': tarikh, 'nerkh_yarane': nerkh_yarane,
                                     'nerkh_azad': nerkh_azad,
                                     'status': 1,
                                     'nerkh_ezterari': nerkh_ezterari,
                                     'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})

                    except Exception as e:
                        return JsonResponse({'status': 3, 'err': str(e)})

                    return JsonResponse({'status': 3})

                sell = SellModel.objects.filter(gs__gsid=data['gsid'], tarikh=data['period'],
                                                product_id=data['product-type']).aggregate(
                    nerkh_yarane=Sum('yarane'), nerkh_azad=Sum('azad'), nerkh_ezterari=Sum('ezterari'),
                    nerkh_azmayesh=Sum('azmayesh'), nerkh_havaleh=Sum('haveleh'), iscrash=Max('iscrash'),
                    sell=Sum('sell'),
                    sumsell=Sum('sellkol'))

                _status = 1
            try:
                isselltype = abs(sell['sumsell'] - sell['sell'])

                if float(isselltype) > 200:

                    if AcceptForBuy.objects.filter(gs__gsid=data['gsid'],
                                                   tarikh=data['period']).count() == 0 and parametr.isacceptforbuy:
                        # title = f"  خطا در خوداظهاری فرآورده  {str(data['period'])} - {str(data['gsid'])}  "
                        # msgs = (f"شماره مکانیکی  دوره  {str(data['period'])}  دارای مغایرت زیاد میباشد ، احتمالا یا شماره "
                        #         f"مکانیکی را وارد نکردید و یا یکی از نازل ها دارای مغایرت میباشد . اگر مغایرت واقعا وجود "
                        #         f"دارد و خطای تایپی نمیباشد با ناحیه تماس بگیرید")
                        # msgid = CreateMsg.objects.create(titel=title, info=msgs, isreply=False, owner_id=5825)
                        # tek = GsList.objects.filter(gs__gsid=data['gsid'], owner__role__role__in=['gs'])
                        # for i in tek:
                        #     ListMsg.objects.create(msg_id=msgid.id, user_id=i.owner_id)
                        return JsonResponse({'status': 6})
                    else:
                        _cg = AcceptForBuy.objects.filter(gs__gsid=data['gsid'],
                                                          tarikh=data['period']).last()
                        if not _cg.ispay:
                            _owner = _cg.owner_id if _cg.owner_id else ''
                            CloseSellReport.objects.create(gs_id=_cg.gs_id, tarikh=data['period'], owner_id=_owner,
                                                           status=6)
                            gsis = data['gsid']
                            nerkh_yarane = 0
                            nerkh_azad = 0
                            nerkh_ezterari = 0
                            nerkh_azmayesh = 0
                            nerkh_havaleh = 0
                            return JsonResponse(
                                {'gsid': gsis, 'date': data['period'], 'nerkh_yarane': nerkh_yarane,
                                 'nerkh_azad': nerkh_azad,
                                 'status': 1,
                                 'nerkh_ezterari': nerkh_ezterari,
                                 'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})

            except (TypeError, AttributeError):
                isselltype = 0

            # if sell['iscrash']:
            #     status = 4

            if gsok.isazadforsell == False:
                # status=9
                gsis = data['gsid']
                nerkh_yarane = 0
                nerkh_azad = 0
                nerkh_ezterari = 0
                nerkh_azmayesh = 0
                nerkh_havaleh = 0
                return JsonResponse(
                    {'gsid': gsis, 'date': data['period'], 'nerkh_yarane': nerkh_yarane,
                     'nerkh_azad': nerkh_azad,
                     'status': 1,
                     'nerkh_ezterari': nerkh_ezterari,
                     'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})
            gsis = data['gsid']
            nerkh_yarane = sell['nerkh_yarane']
            nerkh_azad = sell['nerkh_azad']
            nerkh_ezterari = sell['nerkh_ezterari']
            nerkh_azmayesh = sell['nerkh_azmayesh']
            nerkh_havaleh = sell['nerkh_havaleh']
            nerkh_yarane = nerkh_yarane if nerkh_yarane else 0
            nerkh_azad = nerkh_azad if nerkh_azad else 0
            nerkh_ezterari = nerkh_ezterari if nerkh_ezterari else 0
            nerkh_azmayesh = nerkh_azmayesh if nerkh_azmayesh else 0
            nerkh_havaleh = nerkh_havaleh if nerkh_havaleh else 0
            return JsonResponse(
                {'gsid': gsis, 'date': tarikh, 'nerkh_yarane': nerkh_yarane, 'nerkh_azad': nerkh_azad, 'status': status,
                 'nerkh_ezterari': nerkh_ezterari,
                 'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})

        except ValidationError:
            raise BadRequest(string_assets.INVALID_PARAMETR)

        except KeyError:
            raise BadRequest(string_assets.KeyError)

        except ValueError:
            raise BadRequest(string_assets.ValueError)
        except ObjectDoesNotExist:
            logging.error("Exception occurred", exc_info=True)
            raise BadRequest(string_assets.SELL_DOES_NOT_EXIST)


class GetGsLocation(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        try:
            gs = GsModel.objects.get(gsid=data['gsid'])
            return JsonResponse(
                {'location': gs.location})
        except GsModel.DoesNotExist:
            return JsonResponse({'msg': 'این کد جایگاه وجود ندارد'})


class GetStartDate(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        try:
            gs = GsModel.objects.get(gsid=data['gsid'])
            return JsonResponse(
                {'result': str(gs.start_date)})
        except GsModel.DoesNotExist:
            return JsonResponse({'msg': 'این کد جایگاه وجود ندارد'})


class GetSellInfoAll(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        parametr = Parametrs.objects.all().first()
        _list = []
        data = self.get_data(request.GET)
        _status = 1
        tarikh = data['period']
        # try:
        i = 0
        for item in GsModel.objects.filter(status_id=1, issell=True):
            i += 1
            sell = SellModel.objects.filter(gs__gsid=item.gsid, tarikh=data['period'],
                                            product_id=data['product-type']).aggregate(
                nerkh_yarane=Sum('yarane'), nerkh_azad=Sum('azad'), nerkh_ezterari=Sum('ezterari'),
                sell=Sum('sell'),
                sumsell=Sum('sellkol'),
                nerkh_azmayesh=Sum('azmayesh'), nerkh_havaleh=Sum('haveleh'), iscrash=Max('iscrash'))

            if sell['sumsell']:
                _status = 1
            else:
                if data['product-type'] != 2:
                    sell2 = SellModel.objects.filter(gs__gsid=item.gsid, tarikh=data['period'],
                                                     product_id=2).aggregate(
                        nerkh_yarane=Sum('yarane'))
                    if sell2['nerkh_yarane']:
                        _status = 1
                    else:
                        _status = 2
            # if sell['iscrash']:
            #     _status = 4

            gsis = item.gsid
            nerkh_yarane = sell['nerkh_yarane']
            nerkh_azad = sell['nerkh_azad']
            nerkh_ezterari = sell['nerkh_ezterari']
            nerkh_azmayesh = sell['nerkh_azmayesh']
            nerkh_havaleh = sell['nerkh_havaleh']
            if sell['nerkh_yarane']:
                status = 1
            else:
                status = _status
                nerkh_yarane = 0
                nerkh_azad = 0
                nerkh_ezterari = 0
                nerkh_azmayesh = 0
                nerkh_havaleh = 0

            try:
                isselltype = abs(sell['sumsell'] - sell['sell'])
                if float(isselltype) > 1000 and parametr.isacceptforbuy:
                    status = 6
                    nerkh_yarane = 0
                    nerkh_azad = 0
                    nerkh_ezterari = 0
                    nerkh_azmayesh = 0
                    nerkh_havaleh = 0
            except (TypeError, AttributeError):
                isselltype = 0

            dict = {'gsid': gsis, 'date': tarikh, 'nerkh_yarane': nerkh_yarane, 'nerkh_azad': nerkh_azad,
                    'status': status,
                    'nerkh_ezterari': nerkh_ezterari,
                    'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh}

            _list.append(dict)

        return JsonResponse(
            {'list': _list})

        # except ValidationError:
        #     raise BadRequest(string_assets.INVALID_PARAMETR)
        #
        # except KeyError:
        #     raise BadRequest(string_assets.KeyError)
        #
        # except ValueError:
        #     raise BadRequest(string_assets.ValueError)
        # except ObjectDoesNotExist:
        #     logging.error("Exception occurred", exc_info=True)
        #     raise BadRequest(string_assets.SELL_DOES_NOT_EXIST)


def get_event_ticket(user):
    _min = 0
    jam = 0
    counter = 0

    _list = []
    date_out = datetime.datetime.today()
    date_in = datetime.datetime.today() - datetime.timedelta(days=30)
    for zone in Zone.objects_limit.all():
        result = Ticket.objects.filter(create__gte=date_in, create__lte=date_out,
                                       gs__area__zone_id=zone.id)

        for item in result:

            if item.closedate:
                _min = round(((item.closedate - item.create).seconds / 60))
                jam += int(_min)
                counter += 1

        avg = round(jam / counter)

        _dict = {
            'id': zone.id,
            'name': zone.name,
            'avg': avg
        }

        _list.append(_dict)
        _list = sorted(_list, key=itemgetter('avg'), reverse=False)
        best = _list[0]
        bad = _list[-1]

    r = 0
    for item in _list:
        r += 1
        if item['id'] == user:
            nomre = item['avg']
            rotbe = r
            break
    return ({'bad': bad, 'best': best, 'rotbe': rotbe, 'nomre': nomre})


def get_event_napaydari(user):
    jam = 0
    counter = 0
    _list = []
    date_out = datetime.datetime.today()
    date_in = datetime.datetime.today() - datetime.timedelta(days=10)
    for zone in Zone.objects_limit.all():
        result = Ticket.objects.filter(
            gs__area__zone_id=zone.id, failure_id=1056, is_system=True, create__gte=date_in, create__lte=date_out)

        for item in result:
            if item.closedate:
                _min = round(((item.closedate - item.create).seconds / 60))
                jam += int(_min)
                counter += 1
            else:
                jam += 1000
                counter += 1

        avg = round(jam / counter)

        _dict = {
            'id': zone.id,
            'name': zone.name,
            'avg': avg
        }

        _list.append(_dict)
        _list = sorted(_list, key=itemgetter('avg'), reverse=False)
        best = _list[0]
        bad = _list[-1]

    r = 0
    for item in _list:
        r += 1
        if item['id'] == user:
            nomre = item['avg']
            rotbe = r
            break
    return ({'bad': bad, 'best': best, 'rotbe': rotbe, 'nomre': nomre})


def get_event_dosnotsell(user):
    mylist = []
    rotbe = 0
    nomre = 0
    date_out = datetime.datetime.today()
    date_in = datetime.datetime.today() - datetime.timedelta(days=10)

    for zone in Zone.objects_limit.all():
        gsmodel = GsModel.objects.filter(area__zone_id=zone.id, active=True).count()
        gs = gsmodel * 10
        sell = SellModel.objects.filter(gs__area__zone_id=zone.id, tarikh__gte=date_in, tarikh__lte=date_out).values(
            'gs_id', 'tarikh').annotate(
            tedad=Count('gs_id'))

        if sell.count() > 0:
            _dict = {
                'id': zone.id,
                'name': zone.name,
                'tedad': round((sell.count() / gs) * 100),
            }
            mylist.append(_dict)
    mylist = sorted(mylist, key=itemgetter('tedad'), reverse=True)
    best = mylist[0]
    bad = mylist[-1]
    r = 0
    for item in mylist:
        r += 1
        if item['id'] == user:
            nomre = item['tedad']
            rotbe = r
            break
    return ({'bad': bad, 'best': best, 'rotbe': rotbe, 'nomre': nomre, 'mylist': mylist})


class GetAreaList(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        result = data['myTag']
        x = result.split(',')
        if result:
            for item in x:
                _list.append(int(item))

            areas = Area.objects.filter(zone_id__in=_list)
            srz_data = AreaSerializer(instance=areas, many=True)
            return JsonResponse({'mylist': srz_data.data})
        else:
            return JsonResponse({'mylist': ""})


class GetGsList(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        areas = None
        data = self.get_data(request.GET)
        result = data['myTag']
        x = result.split(',')
        if result:
            for item in x:
                _list.append(int(item))
            if request.user.owner.role.role in ['setad', 'mgr', 'zone']:
                areas = GsModel.objects.filter(area_id__in=_list)
            if request.user.owner.role.role == 'area':
                areas = GsModel.objects.filter(area_id__in=request.user.owner.area_id)
            srz_data = GSSerializer(instance=areas, many=True)
            return JsonResponse({'mylist': srz_data.data})
        else:
            return JsonResponse({'mylist': ""})


class GetDetailTicket(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []

        data = self.get_data(request.GET)
        result = data['myTag']
        x = result.split(',')
        if result:
            for item in x:
                _list.append(int(item))
            failure = FailureSub.objects.filter(failurecategory_id__in=_list)
            srz_data = FailureSerializer(instance=failure, many=True)
            return JsonResponse({'mylist': srz_data.data})
        else:
            return JsonResponse({'mylist': ""})


class GetArzyabiItem(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        base_group_id = data['base_group_id']
        period = data['period']
        for item in BaseDetail.objects.filter(basegroup_id=int(base_group_id)):
            try:
                SathKeyffyat.objects.create(zone_id=request.user.owner.zone_id, period_id=period,
                                            base_detail_id=item.id)
            except ValidationError:
                continue
        result = SathKeyffyat.objects.filter(zone_id=request.user.owner.zone_id, period_id=period,
                                             base_detail__basegroup_id=base_group_id)
        for item in result:
            _dict = {
                'name': item.base_detail.name,
                'value_d1': item.value_d1,
                'value_d2': item.value_d2,
                'result': item.result,
            }
            _list.append(_dict)
        return JsonResponse({'mylist': _list})


class SetArzyabiItem(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        zone = data['zone']
        period = data['period']
        base_detail_id = data['base_detail_id']
        value_d1 = data['value_d1']
        value_d2 = data['value_d2']
        SathKeyffyat.get_input(
            value_d1,
            value_d2,
            period,
            zone,
            base_detail_id,
        )
        _dict = {
            'base_detail_id': base_detail_id
        }
        _list.append(_dict)
        return JsonResponse({'mylist': _list})


class GetLock(BaseAPIView):
    permission_classes = [IsAuthenticated, ]
    _user = None

    def get(self, request):
        data = self.get_data(request.GET)
        _id = data['id']
        ticket = Ticket.objects.get(id=int(_id))
        if ticket.islock:
            _user = Owner.objects.get(id=int(ticket.lockname))
            if int(ticket.lockname) == int(request.user.owner.id):
                me = 1
            else:
                me = 0
            return JsonResponse(
                {'me': me, 'message': '1', 'payam': f'این تیکت در اختیار {str(_user.name), str(_user.lname)}  میباشد '})
        else:
            return JsonResponse({'message': '0'})


class SetLock(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = self.get_data(request.POST)
        val = data['val']
        _id = data['id']
        ticket = Ticket.objects.get(id=int(_id))
        if int(val) == 1:
            ticket.islock = True
            ticket.lockname = str(request.user.owner.id)
            ticket.save()
            return JsonResponse({'message': 'success'})
        else:
            ticket.islock = False
            ticket.lockname = str(request.user.owner.id)
            ticket.save()
            return JsonResponse({'message': 'no'})


class GetGSEdit(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        _list = []
        result = None
        data = self.get_data(request.GET)
        val = int(data['val'])
        _id = int(data['id'])
        _rnd = data['rnd']

        try:
            parametr = GsModel.object_role.c_gsmodel(request).get(id=_id, rnd=_rnd)
            _gsareaid = parametr.area.id
        except GsModel.DoesNotExist:
            return JsonResponse({'message': 'دسترسی غیر مجاز'})

        match val:
            case 1:
                result = Operator.objects.all()
                parametr = parametr.operator_id
            case 2:
                result = Ipc.objects.all()
                parametr = parametr.ipc_id
            case 3:
                result = Rack.objects.all()
                parametr = parametr.rack_id
            case 4:
                result = Modem.objects.all()
                parametr = parametr.modem_id
            case 5:
                result = Status.objects.all()
                parametr = parametr.status_id

            case 6:
                _list = [{'id': 1, 'name': 'آنلاین'}, {'id': 0, 'name': 'آفلاین'}]
                parametr = 1 if parametr.isonline else 0

            case 7:
                _list = [{'id': 1, 'name': 'بلی'}, {'id': 0, 'name': 'خیر'}]
                parametr = 1 if parametr.is_montakhab else 0

            case 8:
                _list = [{'id': 1, 'name': 'انجام شد'}, {'id': 0, 'name': 'موجود نیست'}]
                parametr = 1 if parametr.initial_visit else 0
            case 9:
                _list = [{'id': 1, 'name': 'انجام شد'}, {'id': 0, 'name': 'موجود نیست'}]
                parametr = 1 if parametr.final_visit else 0
            case 10:
                _list = [{'id': 1, 'name': 'بلی'}, {'id': 0, 'name': 'خیر'}]
                parametr = 1 if parametr.isqrcode else 0
            case 11:
                _list = [{'id': 1, 'name': 'دارد'}, {'id': 0, 'name': 'ندارد'}]
                parametr = 1 if parametr.isbank else 0

            case 12:
                _list = [{'id': 1, 'name': 'دارد'}, {'id': 0, 'name': 'ندارد'}]
                parametr = 1 if parametr.ispaystation else 0

            case 13:
                result = GsStatus.objects.all()
                parametr = parametr.gsstatus_id
            case 14:
                _list = [{'id': 1, 'name': 'دارد'}, {'id': 0, 'name': 'ندارد'}]
                parametr = 1 if parametr.isticket else 0
            case 15:
                _list = [{'id': 1, 'name': 'مطلوب'}, {'id': 0, 'name': 'ضعیف'}]
                parametr = 1 if parametr.gpssignal else 0
            case 16:
                _list = [{'id': 1, 'name': 'دارد'}, {'id': 0, 'name': 'ندارد'}]
                parametr = 1 if parametr.isbankmeli else 0
            case 17:
                result = City.objects.filter(area_id=_gsareaid)
                parametr = parametr.city_id

            case 51:
                parametr = parametr.simcart
            case 52:
                parametr = parametr.postal_code
            case 53:
                parametr = str(parametr.telldaftar)
            case 54:
                parametr = parametr.req_equipment
            case 55:
                parametr = parametr.sam
            case 56:
                parametr = parametr.melat_equipment
            case 57:
                parametr = parametr.start_date
            case 58:
                parametr = parametr.name
            case 59:
                parametr = parametr.address
            case 60:
                parametr = parametr.location
            case 61:
                parametr = parametr.m_benzin
            case 62:
                parametr = parametr.m_super
            case 63:
                parametr = parametr.m_naftgaz
            case 64:
                parametr = parametr.tedadnazelmohandesi
            case 95:
                result = Printer.objects.all()
                parametr = parametr.printer_id

            case 96:
                result = ThinClient.objects.all()
                parametr = parametr.thinclient_id

        if result:
            for item in result:
                _dict = {
                    'id': item.id,
                    'name': str(item.name)
                }
                _list.append(_dict)

        if parametr is None:
            parametr = 0

        return JsonResponse({'message': 'success', 'list': _list, 'parametr': parametr})


class SetGSEdit(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _message= 'error'
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        if request.user.owner.role.role in ['mgr', 'setad', 'zone', 'fani', 'area']:
            newname = None
            data = self.get_data(request.GET)
            val = int(data['val'])
            _id = int(data['id'])
            _rnd = data['rnd']
            newval = data['newval']
            try:
                parametr = GsModel.object_role.c_gsmodel(request).get(id=_id, rnd=_rnd)
                _areaid = parametr.area.id
            except GsModel.DoesNotExist:
                return JsonResponse({'message': 'دسترسی غیر مجاز'})
            if request.user.owner.role.role == 'zone' and parametr.area.zone_id != request.user.owner.zone_id:
                return JsonResponse({'message': 'error'})
            if request.user.owner.role.role == 'area' and parametr.area.id != request.user.owner.area_id:
                return JsonResponse({'message': 'error'})

            match val:
                case 1:
                    parametr.operator_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  اپراتور به {newval} ', _id)
                    newname = Operator.objects.get(id=int(newval)).name
                case 2:
                    parametr.ipc_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  سرور به {newval} ', _id)
                    newname = Ipc.objects.get(id=int(newval)).name
                case 3:
                    parametr.rack_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  رک به {newval} ', _id)
                    newname = Rack.objects.get(id=int(newval)).name
                case 4:
                    parametr.modem_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  مودم به {newval} ', _id)
                    newname = Modem.objects.get(id=int(newval)).name
                case 5:
                    parametr.status_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  وضعیت به {newval} ', _id)
                    newname = Status.objects.get(id=int(newval)).name
                case 6:
                    parametr.isonline = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  وضعیت آنلاین به {newval} ', _id)
                    newname = newval
                case 7:
                    parametr.is_montakhab = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  وضعیت منتخب به {newval} ', _id)
                    newname = newval
                case 8:
                    parametr.initial_visit = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  تاریخ بازدید به {newval} ', _id)
                    newname = newval
                case 9:
                    parametr.final_visit = int(newval)
                    parametr.save()
                    newname = newval
                case 10:
                    parametr.isqrcode = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  اجازه اسکن کیوارکد به {newval} ', _id)
                    newname = newval

                case 11:
                    parametr.isbank = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  تجهیزات بانک ملت به {newval} ', _id)
                    newname = newval

                case 12:
                    parametr.ispaystation = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  تجهیزات پی استیشن ملت به {newval} ', _id)
                    newname = newval

                case 13:
                    parametr.gsstatus_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر موقعیت مکانی به {newval} ', _id)
                    newname = GsStatus.objects.get(id=int(newval)).name

                case 14:
                    parametr.isticket = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  مجوز صدور تیکت به {newval} ', _id)
                    newname = newval

                case 15:
                    parametr.gpssignal = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  وضعیت سیگنال به {newval} ', _id)
                    newname = newval

                case 16:
                    parametr.isbankmeli = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  تجهیزات پی استیشن ملی به {newval} ', _id)
                    newname = newval

                case 17:
                    parametr.city_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  شهرستان به {newval} ', _id)
                    newname = City.objects.get(id=int(newval)).name

                case 51:
                    parametr.simcart = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  سیمکارت به {newval} ', _id)
                    newname = newval
                case 52:
                    parametr.postal_code = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  کدپستی به {newval} ', _id)
                    newname = newval
                case 53:
                    parametr.telldaftar = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  تلفن دفتر به {newval} ', _id)
                    newname = newval
                case 54:
                    if len(newval) > 3:
                        parametr.req_equipment = newval
                    else:
                        parametr.req_equipment = None
                    parametr.save()
                    newname = newval
                case 55:
                    if len(newval) > 3:
                        parametr.sam = newval
                    else:
                        parametr.sam = None
                    parametr.save()
                    newname = newval
                case 56:
                    if len(newval) > 3:
                        parametr.melat_equipment = newval
                    else:
                        parametr.melat_equipment = None
                    parametr.save()
                    newname = newval
                case 57:
                    if len(newval) > 3:
                        newval = newval.replace('/', '-')
                        parametr.start_date = newval
                        add_to_log(request, f' ویرایش جایگاه {parametr.gsid} ثبت تاریخ آغاز به فعالیت {newval} ', _id)

                    else:
                        parametr.start_date = None
                    parametr.save()
                    newname = newval
                case 58:
                    if len(newval) > 2:
                        parametr.name = newval
                        add_to_log(request, f' ویرایش جایگاه {parametr.gsid} تغییر نام جایگاه به {newval} ', _id)
                    else:
                        parametr.name = None
                    parametr.save()
                    newname = newval
                case 59:
                    if len(newval) > 3:
                        parametr.address = newval
                        add_to_log(request, f' ویرایش جایگاه {parametr.gsid} تغییر آدرس جایگاه به {newval} ', _id)
                    else:
                        parametr.address = None
                    parametr.save()
                    newname = newval
                case 60:
                    if len(newval) > 3:
                        is_valid, error_message = validate_advanced_location(newval)

                        if not is_valid:
                            return JsonResponse({
                                'message': error_message,
                                'error': error_message
                            })
                        parametr.location = newval
                        add_to_log(request, f' ویرایش جایگاه {parametr.gsid} تغییر لوکیشن جایگاه به {newval} ', _id)
                    else:
                        parametr.location = None
                    parametr.save()
                    newname = newval

                case 61:
                    parametr.m_benzin = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  مخزن بنزین به {newval} ', _id)
                    newname = newval

                case 62:
                    parametr.m_super = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  مخزن سوپر به {newval} ', _id)
                    newname = newval

                case 63:
                    parametr.m_naftgaz = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  مخزن نفتگاز به {newval} ', _id)
                    newname = newval

                case 64:
                    parametr.tedadnazelmohandesi = newval
                    parametr.save()
                    add_to_log(request, f' ویرایش تعداد خرابی مجاز نازل مکانیکی  {parametr.gsid}تغییر   به {newval} ',
                               _id)
                    newname = newval
                case 65:
                    City.objects.create(name=newval, area_id=_areaid)
                    add_to_log(request, f' درج شهرستان جدید  {newval} ', _id)
                case 95:
                    parametr.printer_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  پرینتر به {newval} ', _id)
                    newname = Printer.objects.get(id=int(newval)).name

                case 96:
                    parametr.thinclient_id = int(newval)
                    parametr.save()
                    add_to_log(request, f' ویرایش جایگاه {parametr.gsid}تغییر  thinclient به {newval} ', _id)
                    newname = ThinClient.objects.get(id=int(newval)).name


        else:
            return JsonResponse({'message': _message})

        return JsonResponse({'message': 'success', 'val': val, 'newname': newname})


class SetMarsole(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        newname = None
        data = self.get_data(request.GET)
        val = int(data['val'])
        _id = int(data['id'])
        newval = data['newval']

        parametr = Store.objects.get(id=_id)

        match val:

            case 61:
                if len(newval) > 3:
                    parametr.marsole = newval
                else:
                    parametr.marsole = None
                parametr.save()
                newname = newval

        return JsonResponse({'message': 'success', 'val': val, 'newname': newname})


class GetEditPump(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        data = self.get_data(request.GET)
        val = int(data['val'])
        parametr = Pump.object_role.c_gs(request, 0).get(id=val)
        _liststatuspump = []
        liststatuspan = Statuspump.objects.all()
        statuspan = parametr.status_id
        if liststatuspan:
            for item in liststatuspan:
                _dict = {
                    'id': item.id,
                    'name': item.name
                }
                _liststatuspump.append(_dict)

        _liststatusmodel = []
        liststatusmodel = PumpBrand.objects.all()
        pumpbrand = parametr.pumpbrand_id
        if liststatusmodel:
            for item in liststatusmodel:
                _dict = {
                    'id': item.id,
                    'name': item.name
                }
                _liststatusmodel.append(_dict)

        _listproduct = []
        listproduct = Product.objects.all()
        product = parametr.product_id
        if listproduct:
            for item in listproduct:
                _dict = {
                    'id': item.id,
                    'name': item.name
                }
                _listproduct.append(_dict)

        sakoo = parametr.sakoo
        tolombe = parametr.tolombe
        nazel = parametr.number
        nazelcountshomarande = parametr.nazelcountshomarande

        return JsonResponse({'message': 'success', 'liststatuspump': _liststatuspump, 'statuspan': statuspan,
                             'liststatusmodel': _liststatusmodel, 'pumpbrand': pumpbrand,
                             'listproduct': _listproduct, 'product': product,
                             'nazelcountshomarande': nazelcountshomarande,
                             'sakoo': sakoo, 'tolombe': tolombe, 'nazel': nazel})


class SetEditPump(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
        if owner_p.count() == 0:
            owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                       semat_id=request.user.owner.refrence_id)
        ua = owner_p.get(permission__name='editnazel')
        formpermmision = {}
        for i in owner_p:
            formpermmision[i.permission.name] = i.accessrole.ename
        data = self.get_data(request.GET)
        val = int(data['val'])
        item_pump_status = int(data['item_pump_status'])
        item_pump_status_name = Statuspump.objects.get(id=item_pump_status).name
        item_status_pump = int(data['item_status_pump'])
        item_status_pump_name = PumpBrand.objects.get(id=item_status_pump).name
        item_product_pump = int(data['item_product_pump'])
        item_product_pump_name = Product.objects.get(id=item_product_pump).name
        sakoo_number = int(data['sakoo_number'])
        tolombe_number = int(data['tolombe_number'])
        nazel_number = int(data['nazel_number'])
        nazelcountshomarande = int(data['nazelcountshomarande'])
        parametr = Pump.object_role.c_gs(request, 0).get(id=int(val))
        if formpermmision['editnazel'] in ['create', 'full']:
            parametr.status_id = int(item_pump_status)
            parametr.product_id = int(item_product_pump)
        parametr.pumpbrand_id = int(item_status_pump)
        parametr.sakoo = int(sakoo_number)
        parametr.tolombe = int(tolombe_number)
        parametr.nazelcountshomarande = int(nazelcountshomarande)
        if int(nazel_number) > 0:
            parametr.number = int(nazel_number)
            parametr.uniq = str(nazel_number) + "-" + str(parametr.gs_id)
        parametr.save()
        gs = GsModel.object_role.c_gsmodel(request).get(id=int(parametr.gs_id))
        for item in Product.objects.all():
            if Pump.objects.filter(product_id=item.id, status__status=True, gs_id=parametr.gs_id).count() > 0:
                gs.product.add(Product.objects.get(id=item.id))
            else:
                gs.product.remove(Product.objects.get(id=item.id))
        add_to_log(request, f' ویرایش نازل {nazel_number}جایگاه {parametr.gs.gsid} ', parametr.gs.id)
        return JsonResponse({'message': 'success', 'val': val, 'item_pump_status_name': item_pump_status_name,
                             'item_status_pump_name': item_status_pump_name,
                             'item_product_pump_name': item_product_pump_name,
                             'sakoo_number': sakoo_number,
                             'tolombe_number': tolombe_number,
                             'nazel_number': nazel_number})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def serach_results(request):
    _roleid = zoneorarea(request)
    res = 'چیزی یافت نشد'
    onlyaddres = False
    _gslist = []
    if is_ajax(request=request):
        st = 'gs'
        result = request.GET.get('result')
        if result.isnumeric() == False or len(result) == 4:
            st = 'gs'
            qs = GsModel.object_role.c_gsmodel(request).filter(
                Q(gsid__exact=result) | Q(name__icontains=result))[:6]
            if len(qs) > 0 and len(result) > 0:
                data = []
                for pos in qs:
                    if pos.status_id == 1:
                        status_code = 'success'
                    else:
                        status_code = 'dark'
                    item = {
                        'pk': pos.pk,
                        'gsid': pos.gsid,
                        'name': pos.name,
                        'status': pos.status.name,
                        'status_code': status_code,
                        'nahye': " از ناحیه " + str(pos.area.name) + " در منطقه " + str(pos.area.zone.name)
                    }
                    data.append(item)
                    onlyaddres = False
                    res = data

            if len(qs) == 0 and len(result) == 4:
                qs = GsModel.objects.filter(
                    gsid__exact=result)
                data = []
                for pos in qs:
                    if pos.status_id == 1:
                        status_code = 'success'
                    else:
                        status_code = 'dark'
                    item = {
                        'pk': pos.pk,
                        'gsid': pos.gsid,
                        'name': pos.name,
                        'status': pos.status.name,
                        'status_code': status_code,
                        'nahye': " از ناحیه " + str(pos.area.name) + " در منطقه " + str(pos.area.zone.name)
                    }
                    data.append(item)
                    res = data
                    onlyaddres = True

        if len(result) == 10 or len(result) == 11:
            st = 'owner'
            qs = Owner.object_role.c_owner(request).filter(
                Q(codemeli__exact=result) | Q(mobail__exact=result))[:6]

            if len(qs) > 0 and len(result) > 0:
                data = []
                for pos in qs:
                    if pos.role.role in ['gs', 'tek']:
                        gslist = GsList.objects.filter(owner=pos.id)
                        for item in gslist:
                            _gslist.append(str(item.gs.gsid) + " (" + str(item.gs.name) + ") | ")
                    if pos.active:
                        active = 'فعال'
                        status_code = 'success'
                    else:
                        active = 'غیرفعال'
                        status_code = 'dark'
                    item = {
                        'pk': pos.id,
                        'name': pos.name + " " + pos.lname,
                        'mobail': pos.mobail,
                        'codemeli': pos.codemeli,
                        'active': active,
                        'status_code': status_code,
                        '_gslist': _gslist,
                        'nahye': " در نقش " + str(pos.role.name) + " و سمت " + str(pos.refrence.name)
                    }
                    data.append(item)
                    res = data
        if len(result) > 4 and len(result) < 10:
            st = 'ticket'
            qs = Ticket.object_role.c_gs(request.user.owner.role.role, _roleid).filter(
                Q(id__exact=result))
            if len(qs) > 0 and len(result) > 0:
                data = []
                for pos in qs:
                    item = {
                        'pk': pos.pk,
                        'gsid': pos.gs.gsid,
                        'name': pos.gs.name,
                        'nahye': " شرح خرابی " + str(pos.failure.info) + " در وضعیت " + str(pos.status.info)
                    }
                    data.append(item)
                    res = data

            add_to_log(request, 'جستجو جایگاه ' + str(result), 0)

    return JsonResponse({'data': res, 'st': st, 'onlyaddres': onlyaddres})
    # return JsonResponse({})


class RepairDate(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        create_date = data['tarikh']
        store = int(data['store'])
        create_date = create_date.replace("/", '-')
        tarikh = create_date.split("-")
        tarikh = jdatetime.date(day=int(tarikh[2]), month=int(tarikh[1]), year=int(tarikh[0])).togregorian()
        result = Repair.objects.filter(storage_id=int(store), tarikh=tarikh)
        for item in result:
            _dict = {
                'store': item.repairstore.name,
                'store_id': item.repairstore_id,
                'svalue': item.valuecount,
            }
            _list.append(_dict)

        return JsonResponse({'message': 'success', 'list': _list})


class GetSendSms(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        param1 = data['param1'] if data['param1'] else "0"
        param2 = data['param2'] if data['param2'] else "0"
        param3 = data['param3'] if data['param3'] else "0"

        resp = SendOTP2(data['phone_number'], data['message'], param1, param2, param3)
        return JsonResponse({'resp': resp})


class SendOtpToMalek(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        if Parametrs.objects.first().bypass_sms == False:
            data = self.get_data(request.GET)
            codemeli = data['codemeli']
            mobail = data['mobail']
            codemeli = checknumber(codemeli)
            mobail = checknumber(mobail)
            createotp(mobail, 3)
            return JsonResponse({'message': 'sendotp'})
        return JsonResponse({'message': 'bypassmode'})


class GsInformation(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        gs = []
        _id = (request.GET.get('gsid'))
        # if len(_id) == 3:
        #     _id = "0" + str(_id)
        # if len(_id) == 2:
        #     _id = "00" + str(_id)
        # if len(_id) == 1:
        #     _id = "000" + str(_id)
        # print(_id)
        ticket = Ticket.object_role.c_gs(request, 0).get(id=_id)
        gsitem = IpcLog.objects.get(gs_id=ticket.gs_id)
        cmodem = 'متصل' if gsitem.modem else 'عدم ارتباط'
        operator = gsitem.gs.operator.name if gsitem.gs.operator else ''
        sam = 'متصل' if gsitem.sam else 'عدم اتصال'
        datacenter = 'متصل' if gsitem.datacenter else 'عدم ارتباط'
        modemname = gsitem.gs.modem.name if gsitem.gs.modem else 'ثبت نشده'
        ipcname = gsitem.gs.ipc.name if gsitem.gs.ipc else 'ثبت نشده'
        img = gsitem.imagever if gsitem.imagever else 'ثبت نشده'
        if gsitem.rpm_version:
            rpm = gsitem.rpm_version
            rpm = rpm.replace('.', '')
            rpm = rpm.replace('-', '')
        else:
            rpm = 'ثبت نشده'
        dict = {
            'ramzine': gsitem.nowdate(),
            'gsid': gsitem.gs.gsid,
            'name': gsitem.gs.name,
            'endconnection': gsitem.lastdate(),
            'sam': sam,
            'cmodem': cmodem,
            'dc': datacenter,
            'modem': modemname + " (" + operator + ")",
            'ipc': ipcname,
            'img': img,
            'rpm': rpm,
            'blacklist': gsitem.blacklist_version + " (" + gsitem.blacklist_count + ")",
            'status': gsitem.gs.status.name
        }
        gs.append(dict)

        return JsonResponse({'gs': gs})


class GetEventsLogs(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        gs = []
        _id = (request.GET.get('wid'))

        workflowlogs = WorkflowLog.objects.filter(workflow_id=_id)
        for item in workflowlogs:
            dict = {
                'owner': item.owner.name + " " + item.owner.lname,
                'tarikh': item.pdate(),
            }
            gs.append(dict)
        gs = sorted(gs, key=itemgetter('tarikh'), reverse=True)
        return JsonResponse({'gs': gs})


class GsRisk(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _id = request.GET.get('storeid')
        _gsid = request.GET.get('gsid')
        _rpId = request.GET.get('rpId')
        _nazel = int(request.GET.get('nazel'))
        if _nazel < 10:
            _nazel = str("0") + str(_nazel)
        level = 0
        _today = date.today()
        result = StoreList.objects.filter(id=_id).last() if _id != 1 and len(str(_id)) > 0 else 0
        si_ago_sell = _today.today() - datetime.timedelta(days=30)
        serial = 0
        _role = request.user.owner.role.role
        if request.user.owner.refrence.ename == 'tek':
            _role = 'tek'

        if int(_rpId) != 0:
            reply = Reply.objects.get(id=int(_rpId))
            if reply.ispeykarbandi:
                # rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                #                  password=settings.REDIS_PASS)
                if _id != 1 and len(str(_id)) > 0:
                    otp_peykarbandi = generateotp(_gsid, _nazel) if result.statusstore_id == 1 else 0
                else:
                    otp_peykarbandi = generateotp(_gsid, _nazel)

                try:
                    _gs = GsModel.objects.get(gsid=_gsid)
                    Peykarbandylog.objects.create(gs_id=_gs.id, owner_id=request.user.owner.id, code=otp_peykarbandi,
                                                  nazel=_nazel)
                except Exception as e:
                    _gs = GsModel.objects.get(gsid=_gsid)
                    Peykarbandylog.objects.create(gs_id=_gs.id, owner_id=request.user.owner.id, code=str(e),
                                                  nazel=_nazel)
                # ttl = (rd.ttl(otp_peykarbandi))
                # expire_page = ttl * 1000
                # print(expire_page)
            else:
                otp_peykarbandi = '1'

        parametr = Parametrs.objects.all().first()
        if not parametr.ispeykarbandi:
            otp_peykarbandi = 'تا اطلاع بعدی هیچگونه پیکربندی نباید صورت بگیرد.'

        if _id != 1 and len(str(_id)) > 0:
            risk = StoreHistory.objects.filter(store_id=result.id, create__gte=si_ago_sell, create__lte=_today.today(),
                                               status_id=6).count()
            if risk == 0:
                level = 0
            elif risk == 1:
                level = 1
                serial = result.serial
            elif risk == 2:
                level = 2
                serial = result.serial
            else:
                level = 3
                serial = result.serial

        return JsonResponse({'level': level, 'serial': serial, 'otp_peykarbandi': otp_peykarbandi, 'role': _role})


class AlarmsMgr(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        ownerid = request.GET.get('ownerid')
        _list = []
        owner = Owner.objects.get(codemeli=ownerid)
        week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
        two_ago = datetime.datetime.today() - datetime.timedelta(days=2)
        mount_ago = datetime.datetime.today() - datetime.timedelta(days=31)

        sell_week = SellModel.objects.filter(gs__area__zone_id=owner.zone_id,
                                             tarikh__range=(week_ago, two_ago), ).aggregate(Sum('nomojaz'))
        sell_two = SellModel.objects.filter(gs__area__zone_id=owner.zone_id, tarikh=two_ago, ).aggregate(
            Sum('nomojaz'))
        sell_mount = SellModel.objects.filter(gs__area__zone_id=owner.zone_id,
                                              tarikh__range=(mount_ago, two_ago), ).aggregate(Sum('nomojaz'))

        last_login = (datetime.datetime.today() - owner.user.last_login).days if request.user.last_login else 'no'

        dict = {
            'day': sell_two,
            'week': sell_week,
            'mount': sell_mount,
            'last_login': last_login,
        }
        _list.append(dict)

        return JsonResponse({'sell': _list, })


class ListSellApi(APIView):

    def get(self, request):
        mylist = []
        data = request.GET.get('gsid')
        pump = request.GET.get('pump')
        _id = int(data)

        if pump == '0':
            _list = SellGs.objects.filter(gs_id=_id, product_id=2).order_by('-tarikh')[:30]
            if _list.count() == 0:
                _list = SellGs.objects.filter(gs_id=_id, product_id=4).order_by('-tarikh')[:30]

        else:
            getpump = Pump.objects.get(id=int(pump))
            _list = SellGs.objects.filter(gs_id=_id, product_id=getpump.product_id).order_by('-tarikh')[:30]

        for item in _list:
            dict = {

                'tarikh': str(item.tarikh),
            }
            mylist.append(dict)
        # mylist = sorted(mylist, key=itemgetter('tedad'), reverse=False)
        return JsonResponse({'mylist': mylist})


class AddCloseSellApi(APIView):

    def post(self, request):
        msg = 0
        mylist = []
        data = request.POST.get('gsid')
        pump = request.POST.get('pump')
        tarikh = request.POST.get('tarikh')
        owner = request.POST.get('owner')
        shname = request.POST.get('shname')
        info = request.POST.get('info')
        _id = int(data)
        tarikh = tarikh.split("-")
        tarikh = jdatetime.date(day=int(tarikh[2]), month=int(tarikh[1]), year=int(tarikh[0])).togregorian()

        # getpump = Pump.objects.get(id=int(pump))
        try:
            if int(pump) == 0:
                ac = AccessChangeSell.objects.create(gs_id=_id, editor_id=int(owner), tarikh=tarikh,
                                                     user_id=request.user.id, shname=shname, info=info)
            else:
                ac = AccessChangeSell.objects.create(gs_id=_id, editor_id=int(owner), tarikh=tarikh, pump_id=int(pump),
                                                     user_id=request.user.id, shname=shname, info=info)
            add_to_log(request, ' صدور مجوز فروش ' + str(_id), 0)
            msg = 1
            dict = {
                'gsid': ac.gs.gsid,
                'name': ac.gs.name,
                'tarikh': ac.tarikh,
                'owner': str(ac.editor.name) + " " + str(ac.editor.lname),
                'active': ac.active,
            }
            mylist.append(dict)
        except TypeError as e:
            msg = 0
        # mylist = sorted(mylist, key=itemgetter('tedad'), reverse=False)
        return JsonResponse({'message': msg, 'mylist': mylist})


class TicketEventApi(APIView):

    def get(self, request):
        msg = 0
        mylist = []
        _id = request.GET.get('newid')
        nazel = request.GET.get('nazel')
        sell = SellModel.objects.get(id=_id)
        gsid = sell.gs.id
        tarikh = str(sell.tarikh)

        tarikh = tarikh.split("-")
        tarikh = jdatetime.date(day=int(tarikh[2]), month=int(tarikh[1]), year=int(tarikh[0])).togregorian()
        tarikh2 = tarikh - datetime.timedelta(days=1)
        tarikh3 = tarikh + datetime.timedelta(days=1)
        list = Ticket.objects.filter(closedate__range=(tarikh2, tarikh), gs_id__exact=gsid, Pump_id__exact=nazel)

        for item in list:
            dict = {
                'gsid': item.gs.gsid,
                'name': item.gs.name,
                'tarikh': item.edate(),
                'info': item.failure.info,
                'pomp': item.Pump.number,

            }
            mylist.append(dict)
        list = SellModel.objects.filter(tarikh__range=(tarikh2, tarikh3), gs_id__exact=gsid,
                                        tolombeinfo_id__exact=nazel).order_by('tarikh')
        _list2 = SellModel.objects.filter(tarikh=tarikh, gs_id__exact=gsid,
                                          tolombeinfo_id__exact=nazel).order_by('tarikh').last()
        if _list2 is not None and _list2.mindatecheck and _list2.mindatecheck != '0':
            dict = {
                'tarikh': _list2.mindatecheck,
                'info': 'تاریخ و ساعت اولین سوختگیری',
            }
            mylist.append(dict)
        i = 0
        for item in list:
            if i == 0:
                dict = {
                    'tarikh': item.ekhtelaf,
                    'info': 'اختلاف فروش روز قبل',
                }
                mylist.append(dict)
            if i == 2:
                dict = {
                    'tarikh': item.ekhtelaf,
                    'info': 'اختلاف فروش روز بعد',
                }
                mylist.append(dict)
            i += 1
        mylist2 = []
        list2 = InfoEkhtelafLogs.objects.filter(pomp_id=nazel, tarikh=tarikh).order_by('-id')
        for item in list2:
            if item.status == 1:
                _info = 'جبران فروش از روز بعد '
            if item.status == 2:
                _info = 'جبران فروش از روز قبل '
            if item.status == 3:
                _info = 'اشتباه در ثبت شمارنده مکانیکی '
            if item.status == 4:
                _info = 'اشکالات مکانیکی '
            if item.status == 5:
                _info = 'پرش شمارنده الکترونیکی '
            if item.status == 6:
                _info = 'خرابی کارتخوان، رفتن برق و... '
            dict = {
                'tarikh': str(item.tarikh),
                'info': str(_info) + " " + str(item.amount) + " لیتر",
                'amount': str(item.owner),
            }
            mylist2.append(dict)
        return JsonResponse({'message': msg, 'mylist': mylist, 'mylist2': mylist2})


class AddEventApi(APIView):

    def post(self, request):
        issave = True
        _id = request.POST.get('newid')

        _status = request.POST.get('status')
        _amount = request.POST.get('amount')
        if len(_amount) == 0:
            _amount = 0
            issave = False
        sell = SellModel.objects.get(id=_id)
        info = InfoEkhtelafLogs.objects.filter(pomp_id=sell.tolombeinfo_id, tarikh=sell.tarikh)
        if info.count() > 0:
            info = info.first()
            info.amount = _amount
            info.status = _status
            info.save()
        else:
            InfoEkhtelafLogs.objects.create(pomp_id=sell.tolombeinfo_id, tarikh=sell.tarikh,
                                            owner_id=request.user.owner.id, status=_status, amount=_amount,
                                            sell_id=sell.id)
        if issave:
            sell.nomojaz = _amount
            sell.save()
        return JsonResponse({'message': 'ok'})


class DellEventApi(APIView):

    def post(self, request):
        _id = request.POST.get('newid')
        sell = SellModel.objects.get(id=_id)
        InfoEkhtelafLogs.objects.filter(pomp_id=sell.tolombeinfo_id, tarikh=sell.tarikh).delete()
        sell.nomojaz = sell.nomojaz2
        sell.save()
        return JsonResponse({'message': 'ok'})


def checkproduct():
    for gs in GsModel.objects.all():
        for item in Product.objects.all():
            if Pump.objects.filter(product_id=item.id, status__status=True, gs_id=gs.id).count() > 0:
                gs.product.add(Product.objects.get(id=item.id))
            else:
                gs.product.remove(Product.objects.get(id=item.id))
    return JsonResponse({'ok': 'ok'})


class GetSellInfoWeb(APIView):

    def post(self, request):
        parametr = Parametrs.objects.all().first()
        period = request.POST.get('period')
        tarikh = period
        gsid = request.POST.get('gsid')
        _product = request.POST.get('product-type')
        status = 1
        select = period.split("/")
        period = jdatetime.date(day=int(select[2]), month=int(select[1]),
                                year=int(select[0])).togregorian()
        SellModel.objects.filter(gs__gsid=gsid, product_id__isnull=True).delete()
        try:
            _sellcount = SellModel.objects.filter(gs__gsid=gsid, tarikh=period, islocked=False).count()
            if _sellcount > 0:
                return JsonResponse({'status': 12})
            gsok = GsModel.objects.get(gsid=gsid)
            if gsok.issell == False:
                return JsonResponse({'status': 2})
            if gsok.isazadforsell == False:
                gsis = gsid
                nerkh_yarane = 0
                nerkh_azad = 0
                nerkh_ezterari = 0
                nerkh_azmayesh = 0
                nerkh_havaleh = 0
                return JsonResponse(
                    {
                        'status': 1,
                    })

            gsok = gsok.gsid



        except GsModel.DoesNotExist:
            return JsonResponse({'status': 2})

        # try:

        if period:
            sellcount = SellModel.objects.filter(gs__gsid=gsid, tarikh=period).count()

            if sellcount == 0:

                try:
                    _date = []
                    end_date = CloseGS.objects.filter(gs__gsid=gsid,
                                                      ).order_by('-id')

                    for item in end_date:
                        if period >= item.date_in and period <= item.date_out:
                            gsis = gsid
                            nerkh_yarane = 0
                            nerkh_azad = 0
                            nerkh_ezterari = 0
                            nerkh_azmayesh = 0
                            nerkh_havaleh = 0

                            return JsonResponse(
                                {'gsid': gsis, 'date': tarikh, 'nerkh_yarane': nerkh_yarane,
                                 'nerkh_azad': nerkh_azad,
                                 'status': 11,
                                 'nerkh_ezterari': nerkh_ezterari,
                                 'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})


                except:
                    return JsonResponse({'status': 3})

                return JsonResponse({'status': 3})

            sell = SellModel.objects.filter(gs__gsid=gsid, tarikh=period,
                                            product_id=_product).aggregate(
                nerkh_yarane=Sum('yarane'), nerkh_azad=Sum('azad'), nerkh_ezterari=Sum('ezterari'),
                nerkh_azmayesh=Sum('azmayesh'), nerkh_havaleh=Sum('haveleh'), iscrash=Max('iscrash'),
                sell=Sum('sell'),
                sumsell=Sum('sellkol'))

            _status = 1
        try:
            isselltype = abs(sell['sumsell'] - sell['sell'])
            if float(isselltype) > 1000:
                if AcceptForBuy.objects.filter(gs__gsid=gsid,
                                               tarikh=period).count() == 0 and parametr.isacceptforbuy:
                    return JsonResponse({'status': 6})
        except (TypeError, AttributeError):
            isselltype = 0

        # if sell['iscrash']:
        #     status = 4

        gsis = gsid
        nerkh_yarane = sell['nerkh_yarane']
        nerkh_azad = sell['nerkh_azad']
        nerkh_ezterari = sell['nerkh_ezterari']
        nerkh_azmayesh = sell['nerkh_azmayesh']
        nerkh_havaleh = sell['nerkh_havaleh']
        nerkh_yarane = nerkh_yarane if nerkh_yarane else 0
        nerkh_azad = nerkh_azad if nerkh_azad else 0
        nerkh_ezterari = nerkh_ezterari if nerkh_ezterari else 0
        nerkh_azmayesh = nerkh_azmayesh if nerkh_azmayesh else 0
        nerkh_havaleh = nerkh_havaleh if nerkh_havaleh else 0

        return JsonResponse(
            {'gsid': gsis, 'date': tarikh, 'nerkh_yarane': nerkh_yarane, 'nerkh_azad': nerkh_azad, 'status': status,
             'nerkh_ezterari': nerkh_ezterari,
             'nerkh_azmayesh': nerkh_azmayesh, 'nerkh_havaleh': nerkh_havaleh})

        # except ValidationError:
        #     raise BadRequest(string_assets.INVALID_PARAMETR)
        #
        # except KeyError:
        #     raise BadRequest(string_assets.KeyError)
        #
        # except ValueError:
        #     raise BadRequest(string_assets.ValueError)
        # except ObjectDoesNotExist:
        #     logging.error("Exception occurred", exc_info=True)
        #     raise BadRequest(string_assets.SELL_DOES_NOT_EXIST)


class GetLatoLong(APIView):

    def post(self, request):
        _id = request.POST.get('val')
        _lat = request.POST.get('lat')
        _long = request.POST.get('long')
        _work = Workflow.objects.get(id=_id)
        _work.lat = _lat
        _work.lang = _long
        _work.save()
        return JsonResponse({'message': 'ok'})


class GetPanEdit(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        result = None
        data = self.get_data(request.GET)
        val = int(data['val'])
        pan = PanModels.objects.get(id=val).pan
        return JsonResponse({'message': 'success', 'val': pan, })


class SetPanEdit(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        newname = None
        data = self.get_data(request.GET)
        val = int(data['val'])
        newval = data['newval']

        pan = PanModels.objects.get(id=val)
        pan.oldpan = pan.pan
        pan.pan = int(newval)
        pan.save()
        PanHistory.objects.create(user=request.user, pan_id=pan.id, status_id=pan.statuspan_id,
                                  detail=f' پن از شماره {pan.oldpan} به {newval} ویرایش شد')
        add_to_log(request, f' ویرایش پن کارت جامانده {pan.oldpan}تغییر  اپراتور به {newval} ', pan.gs.id)
        newname = newval
        return JsonResponse({'message': 'success', 'val': val, 'newname': newname})


class CloseSell(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        gs = int(data['val'])
        tarikh = data['tarikh']
        tarikh3 = data['tarikh']
        tarikhnew = None
        if "/" in tarikh3:
            tarikh3 = tarikh3.replace('/', '-')
        try:
            tarikh2 = tarikh.split("/")
            tarikh = jdatetime.date(day=int(tarikh2[2]), month=int(tarikh2[1]), year=int(tarikh2[0])).togregorian()
        except:
            tarikh2 = tarikh.split("-")
            tarikh = jdatetime.date(day=int(tarikh2[2]), month=int(tarikh2[1]), year=int(tarikh2[0])).togregorian()
        tarikhnew = tarikh + datetime.timedelta(days=1)

        active_pumps = Pump.objects.filter(gs_id=gs, status__status=True)
        recorded_pumps = SellModel.objects.filter(gs_id=gs, tarikh=tarikh).values_list('tolombeinfo_id', flat=True)

        # نازل‌هایی که فعال هستند ولی فروش ثبت نشده
        missing_pumps = active_pumps.exclude(id__in=recorded_pumps)

        # ایجاد رکورد برای نازل‌های گمشده
        for pump in missing_pumps:
            # یافتن آخرین رکورد این نازل در روز قبل
            prev_day_record = SellModel.objects.filter(
                gs_id=gs,
                tolombeinfo_id=pump.id,
                tarikh__lt=tarikh
            ).order_by('-tarikh').first()
            start_counter = prev_day_record.start if prev_day_record else 0
            if start_counter > 0:
                SellModel.objects.create(
                    gs_id=gs,
                    tolombeinfo=pump,
                    pumpnumber=pump.number,
                    start=start_counter,
                    end=start_counter,  # چون فروشی نداشته، همان مقدار شروع را به عنوان پایان ثبت می‌کنیم
                    sell=0,
                    tarikh=tarikh,
                    product=pump.product,
                    islocked=True,
                    uniq=f'{tarikh}-{gs}-{pump.id}'

                )

        if SellModel.objects.filter(gs_id=gs, tarikh=tarikh, is_change_counter=True,
                                    is_soratjalase=False).count() > 0:
            return JsonResponse({'message': 'changecounter', })
        sellmodel = SellModel.objects.filter(gs_id=gs, tarikh=tarikh)
        for sell in sellmodel:

            sell.islocked = True
            tid = sell.tolombeinfo_id
            sell.save()
            _result = SellModel.objects.filter(gs_id=gs, tarikh=tarikhnew, tolombeinfo_id=tid).last()

            if _result and sell.start == _result.end:
                _result.mogh = 0
                _result.save()

        OpenCloseSell.create_log(request.user.owner.id, tarikh3, gs, 'close')
        return JsonResponse({'message': 'success', })


class OpenSell(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        gs = int(data['val'])
        tarikh = data['tarikh']
        tarikh3 = data['tarikh']
        add_to_log(request, f" باز کردن  حساب فروش جایگاه {gs} در تاریخ {tarikh}", 0)
        SellModel.objects.filter(gs_id=gs, tarikh=tarikh).update(islocked=False)
        OpenCloseSell.create_log(request.user.owner.id, tarikh3, gs, 'open')
        return JsonResponse({'message': 'success', })


class ListNazelInfo(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        serial = data['serial']
        _statusref = StatusRef.objects.all()
        for ref in _statusref:
            _dict = {
                'id': ref.id,
                'name': ref.name
            }
            _list.append(_dict)
        if len(serial) >= 4:
            try:
                _status = StoreList.objects.get(serial=serial)
                if _status.statusstore_id == 1:
                    gss = Pump.objects.filter(master=serial).last()
                else:
                    gss = Pump.objects.filter(pinpad=serial).last()

                if gss:
                    return JsonResponse({'message': 'success', 'zoneid': str(gss.gs.area.zone.id), 'mylist': _list,
                                         'zonename': str(gss.gs.area.zone.name),
                                         'gs_id': str(gss.gs.id),
                                         'gsid': str(gss.gs.gsid),
                                         'gsname': str(gss.gs.name),
                                         'nazelid': str(gss.id),
                                         'nazelnumber': str(gss.number),
                                         'serial': serial,
                                         'statusref': _status.status_id,
                                         'nazelname': str(gss.product.name)})
                else:
                    return JsonResponse({'message': 'success', 'mylist': _list, })
            except StoreList.DoesNotExist:
                return JsonResponse({'message': 'success', 'mylist': _list, })
        else:
            return JsonResponse({'message': 'error'})


class ListGsByZoneId(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        zone = int(data['zone'])
        gss = GsModel.objects.filter(area__zone_id=zone)
        for item in gss:
            dict = {
                'id': str(item.id),
                'gsid': str(item.gsid),
                'name': str(item.name)
            }
            _list.append(dict)
        return JsonResponse({'message': 'success', 'mylist': _list})


class ListNazelByGsId(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _list = []
        data = self.get_data(request.GET)
        gs = int(data['gs'])
        gss = Pump.objects.filter(gs_id=gs)
        for item in gss:
            dict = {
                'id': str(item.id),
                'number': str(item.number),
                'name': str(item.product.name),
                'gs': str(item.gs.name)
            }
            _list.append(dict)
        return JsonResponse({'message': 'success', 'mylist': _list})


class SaveChangeNazel(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)
        serial = data['serial']
        _sname = data['sname']
        nazel = int(data['nazel_id'])
        sname = GenerateSerialNumber.objects.get(id=_sname)
        pump = Pump.objects.get(id=nazel)
        try:
            _status = StoreList.objects.get(serial=serial)
        except StoreList.DoesNotExist:
            mystore = StoreList.objects.create(zone_id=pump.gs.area.zone_id, serial=serial, owner_id=request.user.id,
                                               statusstore_id=sname.status_id, pump_id=nazel, gs_id=pump.gs_id,
                                               status_id=5, uniq=str(serial) + '-' + str(sname.status_id))
            StoreHistory.objects.create(store_id=mystore.id, owner_id=request.user.owner.id, baseroot=0,
                                        information="ایجاد قطعه جهت چاپ سریال جدید ",
                                        status_id=5, description=f' ',
                                        )

        allserial = Pump.objects.filter(master=serial)
        for item in allserial:
            item.master = ""
            item.save()
        allserial = Pump.objects.filter(pinpad=serial)
        for item in allserial:
            item.pinpad = ""
            item.save()

        if sname.status_id == 1:
            pump.master = serial
        else:
            pump.pinpad = serial

        pump.save()

        return JsonResponse({'message': 'success', })


class ShowImgTek(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):

        _list = []
        data = self.get_data(request.POST)
        _id = data['id']
        val = data['val']

        if val == "1":
            ownerfiles = OwnerFiles.objects.get(imageid=_id)
            ownerfiles = ownerfiles.img.url
        if val == "2":
            ownerfiles = OwnerChild.objects.get(imageid=_id)
            ownerfiles = ownerfiles.img.url
        if val == "3":
            ownerfiles = ImgSerial.objects.get(id=_id)
            ownerfiles = ownerfiles.img.url
        if val == "4":
            ownerfiles = CreateMsg.objects.get(id=_id)
            ownerfiles = ownerfiles.attach.url
        if val == "5":
            ownerfiles = GsModel.objects.get(id=_id)
            ownerfiles = ownerfiles.koroki.url

        if val == "6":
            ownerfiles = GsModel.objects.get(id=_id)
            ownerfiles = ownerfiles.sejelli.url

        return JsonResponse({'message': 'success', 'ownerfiles': ownerfiles})


class AreaInZone(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)

        val = data['zoneid']
        _city = Area.objects.filter(zone_id=val)
        for city in _city:
            dict = {
                'id': city.id,
                'name': city.name
            }
            _list.append(dict)
        gs_list = []
        _gs_list = GsModel.object_role.c_gsmodel(request).filter(area__zone_id=val)
        for item in _gs_list:
            gs_list.append({
                'id': item.id,
                'gsid': str(item.gsid),
                'name': str(item.name)
            })
        return JsonResponse({'message': 'success', 'mylist': _list, 'gs_list': gs_list})


class GsInCity(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = self.get_data(request.POST)

        val = data['cityid']
        area = data['areaid']

        gs_list = []
        if val == "0":
            _gs_list = GsModel.object_role.c_gsmodel(request).filter(area_id=area)
        else:
            _gs_list = GsModel.object_role.c_gsmodel(request).filter(city_id=val)
        for item in _gs_list:
            gs_list.append({
                'id': item.id,
                'gsid': str(item.gsid),
                'name': str(item.name)
            })
        return JsonResponse({'message': 'success', 'gs_list': gs_list})


class CityInArea(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)

        val = data['areaid']
        zoneid = data['zoneid']
        _city = City.objects.filter(area_id=val)
        for city in _city:
            dict = {
                'id': city.id,
                'name': city.name
            }
            _list.append(dict)
        gs_list = []
        if val == "0":
            _gs_list = GsModel.object_role.c_gsmodel(request).filter(area__zone_id=zoneid)
        else:
            _gs_list = GsModel.object_role.c_gsmodel(request).filter(area_id=val)

        for item in _gs_list:
            gs_list.append({
                'id': item.id,
                'gsid': str(item.gsid),
                'name': str(item.name)
            })
        return JsonResponse({'message': 'success', 'mylist': _list, 'gs_list': gs_list})


class AddRemoveLock(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.owner.role.role in ['zone', 'tek']:
            _role = 'smart'
        elif request.user.owner.role.role in ['engin']:
            _role = 'engin'
        elif request.user.owner.refrence.ename == 'tek':
            _role = 'smart'
        _list = []
        _serial = ""
        data = self.get_data(request.POST)
        msg = 'success'
        val = data['val']
        status = int(data['status'])
        serial = data['serial']
        meetingnumber = data['meetingnumber']
        serial = checknumber(serial)
        isserial = validate_serial_format(serial)
        if not isserial:
            msg = f'فرمت شماره سریال مشکل دارد'
            return JsonResponse({'message': msg, })
        _ticket = Ticket.objects.get(id=val)
        if _ticket.failure.failurecategory in [1010, 1011]:
            pid = "1"
        else:
            pid = "2"

        if status == 1:
            _lock = LockModel.objects.get(serial=serial.upper(), owner_id=request.user.owner.id, status_id=8)
            _lock.ticket_id = _ticket.id
            _lock.pump_id = _ticket.Pump_id
            _lock.meeting_number = meetingnumber
            _lock.gs_id = _ticket.gs_id
            _lock.position_id = pid
            _lock.status_id = 5
            _lock.ename = _role
            _lock.send_date_gs = datetime.datetime.today()
            _lock.sdg_user_id = request.user.id
            _serial = _lock.serial

            _info = f' نصب در جایگاه {_lock.gs.name}' if pid == "2" else f' نصب در جایگاه {_lock.gs.name} و نازل {_lock.pump.number}'
            _lock.save()
            LockLogs.objects.create(
                status_id=5,
                owner_id=request.user.id,
                lockmodel_id=_lock.id,
                gs_id=_ticket.gs_id,
                info=_info,
                pump_id=_ticket.Pump_id)
        elif status == 2:
            try:
                _lock = LockModel.objects.get(serial=serial.upper(), zone_id=request.user.owner.zone_id,
                                              status_id__in=[4, 5, 8])
                if _lock.gs.id == _ticket.gs.id:
                    _lock.ticket2 = _ticket.id
                    _lock.ename = _role
                    _lock.gs_id = _ticket.gs_id
                    _lock.meeting_number = meetingnumber
                    _lock.status_id = 6
                    _serial = _lock.serial
                    _lock.input_date_gs = datetime.datetime.today()
                    _lock.idg_user_id = request.user.id
                    _info = f' فک از جایگاه {_lock.gs.name}' if pid == "2" else f'  فک از جایگاه {_lock.gs.name} و نازل {_lock.pump.number}'
                    _lock.save()
                    LockLogs.objects.create(
                        status_id=6,
                        owner_id=request.user.id,
                        lockmodel_id=_lock.id,
                        gs_id=_ticket.gs_id,
                        info=_info,
                        pump_id=_ticket.Pump_id)
                else:
                    msg = f'این پلمپ بر روی جایگاه دیگری نصب شده بود'
            except LockModel.DoesNotExist:
                _count_lock = LockModel.objects.filter(serial=serial.upper()).count()
                if _count_lock > 0:
                    _lock = LockModel.objects.get(serial=serial.upper())
                    msg = f'وضعیت قطعه باید ابتدا نصب در تلمبه باشد در حال حاضر وضعیت قطعه  {_lock.status} میباشد '
                else:
                    numbers, letters = separate_numbers_and_letters(serial)
                    _seri = letters.upper() if len(letters) > 0 else "##"
                    _locknew = LockModel.objects.create(zone_id=request.user.owner.zone_id,
                                                        idg_user_id=request.user.id,
                                                        input_date_gs=datetime.datetime.today(),
                                                        owner_id=request.user.owner.id,
                                                        serial=str(serial.upper()),
                                                        ticket2=_ticket.id,
                                                        ename=_role,
                                                        serial_number=int(numbers), status_id=6,
                                                        pump_id=_ticket.Pump_id,
                                                        gs_id=_ticket.gs_id,
                                                        meeting_number=meetingnumber,
                                                        manualadd=1
                                                        )
                    _serial = _locknew.serial

        elif status == 3:
            _lock = LockModel.objects.get(serial=serial.upper(), owner_id=request.user.owner.id, status_id=5)
            _name = _lock.gs.name
            try:
                _pump = 0 if _lock.position_id == 2 else _lock.pump.number
            except:
                _pump = 0
            _lock.ticket_id = None
            _lock.pump_id = None
            _lock.gs_id = None
            _lock.meeting_number = None
            _lock.position_id = None
            _lock.send_date_gs = None
            _lock.sdg_user_id = None
            _lock.status_id = 8
            _serial = _lock.serial
            _info = f'واگرد از نصب، جایگاه {_name}' if pid == "2" else f'واگرد از نصب، جایگاه {_name} و نازل {_pump}'
            _lock.save()
            LockLogs.objects.create(
                status_id=8,
                owner_id=request.user.id,
                lockmodel_id=_lock.id,
                gs_id=_ticket.gs_id,
                info=_info,
                pump_id=_ticket.Pump_id)

        elif status == 4:
            try:
                _lock = LockModel.objects.get(serial=serial.upper(), status_id=6)
                _lid = _lock.id
                if _lock.manualadd == 1:
                    _serial = _lock.serial
                    _lock.delete()
                else:
                    _lock.input_date_gs = None
                    _lock.idg_user_id = None
                    _lock.status_id = 5
                    _lock.meeting_number = None
                    _serial = _lock.serial
                    _info = f'واگرد از فک، جایگاه {_lock.gs.name}' if pid == "2" else f'واگرد از فک، جایگاه {_lock.gs.name} و نازل {_lock.pump.number}'
                    _lock.save()
                    LockLogs.objects.create(
                        status_id=5,
                        owner_id=request.user.id,
                        lockmodel_id=_lid,
                        gs_id=_ticket.gs_id,
                        info=_info,
                        pump_id=_ticket.Pump_id)
            except LockModel.DoesNotExist:
                msg = f'وضعیت این قطعه داغی تغییر کرده است'

        polomps = []
        result = LockModel.objects.filter(owner_id=request.user.owner.id, status_id=8)
        for lock in result:
            polomps.append({
                'id': lock.id,
                'serial': lock.serial
            })
        return JsonResponse({'message': msg, 'polomps': polomps, 'serial': str(_serial), 'status': int(status),
                             'ticket': data['val']})


def separate_numbers_and_letters(input_string):
    numbers = ''
    letters = ''

    for char in input_string:
        if char.isdigit():
            numbers += char
        elif char.isalpha():
            letters += char

    return numbers, letters


class RunRemoveLock(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        istek = True if request.user.owner.role.role in ['tek',
                                                         'engin'] or request.user.owner.refrence.ename == 'tek' else False

        installlock = []
        removelock = []
        data = self.get_data(request.POST)

        val = data['val']
        rnd = data['rnd']

        _ticket = Ticket.objects.get(id=val, rnd=rnd)
        gsname = _ticket.gs.name
        try:
            gspump = _ticket.Pump.number
        except:
            gspump = ''

        _lock = LockModel.objects.filter(ticket_id=val, send_date_gs__isnull=False)
        try:
            meetingnumber = _lock.first()
            meetingnumber = meetingnumber.meeting_number
        except:
            meetingnumber = ""
        for item in _lock:
            installlock.append({
                'serial': item.serial,
                'ticket': item.ticket_id
            })
        _lock = LockModel.objects.filter(ticket2=val, input_date_gs__isnull=False)
        for item in _lock:
            removelock.append({
                'serial': item.serial,
                'ticket': item.ticket_id
            })

        position = []
        result = Position.objects.all()
        for lock in result:
            position.append({
                'id': lock.id,
                'name': lock.name,

            })
        polomps = []
        result2 = LockModel.objects.filter(owner_id=request.user.owner.id, status_id=8)
        for lock2 in result2:
            polomps.append({
                'id': lock2.id,
                'serial': lock2.serial,

            })

        return JsonResponse(
            {'message': 'success', 'polomps': polomps, 'removelock': removelock, 'installlock': installlock,
             'meetingnumber': meetingnumber,
             'ticket': data['val'], 'istek': istek, 'position': position, 'gsname': gsname, 'gspump': gspump})


class LockListApi(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    @transaction.atomic
    def post(self, request):
        polomps = []
        data = self.get_data(request.POST)

        val = data['val']
        result = LockModel.objects.filter(owner_id=request.user.owner.id, status_id=8, position_id=val)
        for lock in result:
            polomps.append({
                'id': lock.id,
                'serial': lock.serial,

            })

        return JsonResponse(
            {'message': 'success', 'polomps': polomps, })


class DeleteZonePack(BaseAPIView):
    permission_classes = [IsAuthenticated, ]
    ok = 1

    @transaction.atomic
    def post(self, request):

        ok = 1
        data = self.get_data(request.POST)
        val = data['val']
        inrow = data['inrow']
        if request.user.is_superuser:
            InsertLock.objects.get(id=val).delete()
            return JsonResponse({'message': 'success', 'ok': ok, })
        if inrow == "1":
            lockmodels = LockModel.objects.filter(insertlock_id=val).exclude(status_id=3).count()
            if lockmodels > 0:
                ok = 2
            else:
                ok = 1
                LockModel.objects.filter(insertlock_id=val).delete()
                InsertLock.objects.get(id=val).delete()
        if inrow == "2":
            lockmodels = LockModel.objects.filter(sendposhtiban_id=val).exclude(status_id=4).count()
            if lockmodels > 0:
                ok = 2
            else:
                ok = 1
                _result = LockModel.objects.filter(sendposhtiban_id=val)
                for item in _result:
                    item.status_id = 7
                    item.send_date_poshtiban = None
                    item.sendposhtiban_id = None
                    item.sdp_user_id = None
                    item.save()
                SendPoshtiban.objects.get(id=val).delete()

        return JsonResponse({'message': 'success', 'ok': ok, })


class RunErjaToTek(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        teks = []
        tek = Owner.objects.filter(active=True, role__role='tek', zone_id=request.user.owner.zone_id).exclude(
            id=request.user.owner.id)
        for item in tek:
            teks.append({
                'id': item.id,
                'name': item.name + " " + item.lname
            })
        return JsonResponse(
            {'message': 'success', 'teks': teks, })


class ErjaToTek(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = self.get_data(request.POST)
        val = data['val']
        _user = data['user']
        owner = Owner.objects.get(id=_user)
        name = str(owner.get_full_name())
        _ticket = Ticket.objects.get(id=val, gs__area__zone_id=request.user.owner.zone_id)
        _ticket.usererja = _user
        _ticket.save()
        Workflow.objects.create(ticket_id=val, user_id=request.user.id,
                                description=f' تیکت به {name} منتقل شد ',
                                organization_id=1, failure_id=_ticket.failure.id)
        return JsonResponse(
            {'message': 'success'})


class ShowLock(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    @transaction.atomic
    def post(self, request):
        result = None
        polomps = []
        data = self.get_data(request.POST)

        val = data['val']
        st = data['st']
        if st == "1":
            result = LockModel.objects.filter(status_id=5, pump_id=val)
        elif st == "2":
            result = LockModel.objects.filter(status_id=5, gs_id=val, ticket__failure__enname='rack')
        for lock in result:
            polomps.append({
                'serial': lock.serial,
            })

        return JsonResponse(
            {'message': 'success', 'polomps': polomps, })


class LastSellDore(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = self.get_data(request.POST)
        dore = data['dore']
        nazel = data['nazel']
        datein = dore.split("/")
        dore = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
        _amount = SellModel.objects.filter(tolombeinfo_id=nazel, tarikh__lt=dore).order_by('-tarikh').first()
        amount = _amount.start
        return JsonResponse(
            {'message': 'success', 'amount': amount, 'date': str(_amount.tarikh)})


class GetGsInfoBtmt(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        try:
            gs = GsModel.objects.get(gsid=data['gsid'])
            return JsonResponse(
                {'result': str(gs.start_date),
                 'gsid': str(gs.gsid),
                 'zone_id': str(gs.area.zone.id),
                 'zone_name': str(gs.area.zone.name),
                 'area_id': str(gs.area.id),
                 'area_name': str(gs.area.name),
                 'name': str(gs.name),
                 })
        except GsModel.DoesNotExist:
            return JsonResponse({'msg': 'این کد جایگاه وجود ندارد'})


class SetGsIsPayBtmt(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        gs = GsModel.objects.get(gsid=data['gsid'])
        gs.btmt = True
        gs.save()
        return JsonResponse({'msg': 'ookk'})


class GoAddress(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        # try:
        gs = GsModel.objects.get(id=data['gsid'])

        return JsonResponse({
            'tell': str(gs.telldaftar),
            'gsid': str(gs.gsid),
            'name': str(gs.name),
            'address': str(gs.address),
            'area': str(gs.area.name),
            'zone': str(gs.area.zone.name),
        }
        )
        # except GsModel.DoesNotExist:
        #     return JsonResponse({'msg': 'این کد جایگاه وجود ندارد'})


class GetModemList(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)

        gid = data['gid']
        _st = data['st']

        if _st == '1':
            ipc = IpcLog.objects.get(id=gid)
        else:
            ipc = IpcLogHistory.objects.get(id=gid)
        _result = ModemDisconnect.objects.filter(gs_id=ipc.gs_id, tarikh__year=ipc.updatedate.year,
                                                 tarikh__month=ipc.updatedate.month,
                                                 tarikh__day=ipc.updatedate.day - 1)
        i = 0
        for _ in _result:
            i += 1
            dict = {
                'id': str(i),
                'in': _.starttime,
                'out': _.endtime,
                'ip': _.ip
            }
            _list.append(dict)
        mlist = sorted(_list, key=itemgetter('out'), reverse=False)
        return JsonResponse({'message': 'success', 'mylist': mlist})


def get_semat_for_role(request):
    role_id = request.GET.get('role_id')
    if not role_id:
        return JsonResponse([], safe=False)
    # دریافت سمت‌های منحصر به فرد برای نقش انتخاب شده

    semat_ids = DefaultPermission.objects.exclude(accessrole_id=5).filter(role_id=role_id).values_list('semat_id',
                                                                                                       flat=True).distinct()

    semats = Refrence.objects.filter(id__in=semat_ids).values('id', 'name')

    return JsonResponse(list(semats), safe=False)


class WebhookReceiveWaybill(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            data = json.loads(request.body)

            # بررسی اینکه آیا داده یک لیست است یا یک آبجکت تکی
            if isinstance(data, list):
                return self.process_batch_waybills(data)
            else:
                return self.process_single_waybill(data)

        except json.JSONDecodeError as e:
            return Response(
                {"status": "error", "message": f"Invalid JSON format {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def process_single_waybill(self, data):
        """پردازش یک waybill تکی"""
        waybill_id = data.get('waybill_id')
        send_type = int(data.get('send_type')) if data.get('send_type') else None
        # exit_date = int(data.get('exit_date')) if data.get('exit_date') else None
        # exit_date = to_miladi(exit_date)

        if not waybill_id:
            return Response(
                {"status": "error", "message": "waybill_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not send_type:
            return Response(
                {"status": "error", "message": "send_type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.handle_waybill_operation(data, waybill_id, send_type)

    def process_batch_waybills(self, data_list):
        """پردازش لیستی از waybillها"""
        results = {
            "successful_operations": [],
            "failed_operations": []
        }

        for index, data in enumerate(data_list):
            try:
                waybill_id = data.get('waybill_id')
                send_type = int(data.get('send_type')) if data.get('send_type') else None

                if not waybill_id:
                    results["failed_operations"].append({
                        "index": index,
                        "error": "waybill_id is required",
                        # "data": data
                    })
                    continue

                if not send_type:
                    results["failed_operations"].append({
                        "index": index,
                        "error": "send_type is required",
                        # "data": data
                    })
                    continue

                # پردازش هر waybill
                operation_result = self.handle_single_waybill_operation(data, waybill_id, send_type)

                if operation_result["status"] == "success":
                    results["successful_operations"].append({
                        "index": index,
                        "waybill_id": waybill_id,
                        "operation": operation_result["operation"],
                        # "data": operation_result.get("data")
                    })
                else:
                    results["failed_operations"].append({
                        "index": index,
                        "waybill_id": waybill_id,
                        "error": operation_result.get("message", "Unknown error"),
                        # "data": data
                    })

            except Exception as e:
                results["failed_operations"].append({
                    "index": index,
                    "waybill_id": data.get('waybill_id'),
                    "error": str(e),
                    # "data": data
                })

        # ساخت پاسخ نهایی
        total_operations = len(data_list)
        successful_count = len(results["successful_operations"])
        failed_count = len(results["failed_operations"])

        response_data = {
            "status": "partial_success" if successful_count > 0 and failed_count > 0 else
            "success" if successful_count == total_operations else
            "failed",
            "summary": {
                "total_operations": total_operations,
                "successful_operations": successful_count,
                "failed_operations": failed_count
            },
            "details": results
        }

        status_code = status.HTTP_207_MULTI_STATUS if failed_count > 0 else status.HTTP_200_OK
        return Response(response_data, status=status_code)

    def handle_single_waybill_operation(self, data, waybill_id, send_type):
        """پردازش عملیات بر روی یک waybill"""
        try:
            if 'gsid' in data:
                try:
                    _id = data['gsid']
                    if len(_id) == 3:
                        _id = "0" + str(_id)
                    if len(_id) == 2:
                        _id = "00" + str(_id)
                    if len(_id) == 1:
                        _id = "000" + str(_id)
                    gs_model = GsModel.objects.get(gsid=_id)
                    data['gsid'] = gs_model.id

                except GsModel.DoesNotExist:
                    return {
                        "status": "error",
                        "message": "GSID does not exist"
                    }
            if send_type == 1:  # ایجاد
                serializer = WaybillSerializer(data=data)
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return {
                            "status": "success",
                            "data": serializer.data,
                            "operation": "created"
                        }
                    except IntegrityError as e:
                        # تشخیص خطای تکراری بودن
                        error_msg = str(e)
                        if 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
                            return {
                                "status": "error",
                                "message": "دابلیکیت"
                            }
                        else:
                            return {
                                "status": "error",
                                "message": error_msg
                            }
                else:
                    # بررسی خطاهای validation برای تکراری بودن
                    errors = serializer.errors

                    if 'waybill_id' in errors:
                        for error in errors['waybill_id']:

                            if error.code == 'unique':
                                return {
                                    "status": "error",
                                    "message": "duplicate"
                                }
                            if 'already exists' in str(error).lower() or 'unique' in str(error).lower():
                                return {
                                    "status": "error",
                                    "message": "duplicate"
                                }
                    return {
                        "status": "error",
                        "message": f"Validation failed {errors}",
                        "errors": errors
                    }

            elif send_type in [2, 3]:  # ویرایش
                try:
                    waybill = Waybill.objects.get(waybill_id=waybill_id)
                    serializer = WaybillSerializer(waybill, data=data, partial=True)

                    if serializer.is_valid():
                        serializer.save()
                        return {
                            "status": "success",
                            "data": serializer.data,
                            "operation": "updated"
                        }
                    else:
                        return {
                            "status": "error",
                            "message": "Valida2tion failed",
                            "errors": serializer.errors
                        }
                except Waybill.DoesNotExist:
                    return {
                        "status": "error",
                        "message": "Waybill not found"
                    }

            elif send_type in [4, 5]:  # حذف
                try:
                    waybill = Waybill.objects.get(waybill_id=waybill_id)
                    waybill.delete()
                    return {
                        "status": "success",
                        "message": "Waybill deleted",
                        "operation": "deleted"
                    }
                except Waybill.DoesNotExist:
                    return {
                        "status": "error",
                        "message": "Waybill not found"
                    }

            else:
                return {
                    "status": "error",
                    "message": "Invalid send_type"
                }

        except Exception as e:
            error_msg = str(e)
            if 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
                return {
                    "status": "error",
                    "message": "duplicate"
                }
            return {
                "status": "error",
                "message": error_msg
            }

    # تابع اصلی برای backward compatibility
    def handle_waybill_operation(self, data, waybill_id, send_type):
        result = self.handle_single_waybill_operation(data, waybill_id, send_type)

        if result["status"] == "success":
            return Response(
                {"status": "success", "data": result.get("data"), "operation": result.get("operation")},
                status=status.HTTP_201_CREATED if result.get("operation") == "created" else status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": "error", "message": result.get("message"), "errors": result.get("errors")},
                status=status.HTTP_400_BAD_REQUEST if result.get("message") != "Waybill not found"
                else status.HTTP_404_NOT_FOUND
            )


class GetGsByArea(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        data = self.get_data(request.GET)
        """
        API برای دریافت اطلاعات جایگاه‌ها بر اساس areaid
        پارامتر ورودی: areaid
        خروجی: لیستی از اطلاعات جایگاه‌های مربوط به ناحیه
        """
        areaid = None
        gsid = None
        if 'area' in data:
            areaid = data['area']
        if 'gsid' in data:
            gsid = data['gsid']
        if not areaid and not gsid:
            return Response({'error': 'پارامتر area یا gsid الزامی است'}, status=400)

        try:
            if areaid:
                # دریافت تمام جایگاه‌های مربوط به این ناحیه
                gs_models = GsModel.objects.filter(area__areaid=areaid)
            elif gsid:
                gs_models = GsModel.objects.filter(gsid=gsid)
            else:
                return Response({'error': ' یک gsid یا area واردکنید'}, status=404)

            # ساخت داده‌های خروجی
            result = []
            for gs in gs_models:
                result.append({
                    'zoneid': gs.area.zone.zoneid,
                    'zone_name': gs.area.zone.name,
                    'areaid': gs.area.areaid,
                    'area_name': gs.area.name,
                    'status': gs.status.id,
                    'gsid': gs.gsid,
                    'name': gs.name,
                    'address': gs.address
                })

            return Response({'data': result})

        except Area.DoesNotExist:
            return Response({'error': 'ناحیه یافت نشد'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class RunStore(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        polomps = []
        installlock = []
        removelock = []
        data = self.get_data(request.POST)

        val = data['val']
        rnd = data['rnd']

        _ticket = Ticket.objects.get(id=val, rnd=rnd)
        gsname = _ticket.gs.name
        try:
            gspump = _ticket.Pump.number
        except:
            gspump = ''

        _tek = GsList.objects.filter(gs_id=_ticket.gs_id, owner__role__role='tek', owner__active=True).first()
        _stores = StoreList.objects.filter(getuser_id=_tek.owner.id, status_id=4, assignticket__isnull=True)

        for item in _stores:
            polomps.append({
                'id': item.id,
                'serial': item.serial,
                'status': item.statusstore.name,
            })

        result2 = StoreList.objects.filter(assignticket=_ticket.id)
        for lock2 in result2:
            installlock.append({
                'id': lock2.id,
                'serial': lock2.serial,
                'status': lock2.statusstore.name,

            })

        istek = True if request.user.owner.refrence_id == 1 else False

        return JsonResponse(
            {'message': 'success', 'polomps': polomps, 'removelock': removelock, 'installlock': installlock,
             'ticket': data['val'], 'gsname': gsname, 'gspump': gspump, 'istek': istek})


class AssignStore(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        _serial = ""
        data = self.get_data(request.POST)
        msg = 'success'
        val = data['val']
        status = int(data['status'])
        serial = data['serial']

        serial = checknumber(serial)

        if status == 1:
            _lock = StoreList.objects.get(serial=serial)
            _lock.assignticket = val
            _lock.save()
            serial = _lock.serial
            st = _lock.statusstore.name
        elif status == 2:
            try:
                _lock = StoreList.objects.get(serial=serial)
                _lock.assignticket = None
                _lock.save()
                st = _lock.statusstore.name
            except LockModel.DoesNotExist:
                pass

        polomps = []
        _ticket = Ticket.objects.get(id=val)
        _tek = GsList.objects.filter(gs_id=_ticket.gs_id, owner__role__role='tek', owner__active=True).first()
        _stores = StoreList.objects.filter(getuser_id=_tek.owner.id, status_id=4, assignticket__isnull=True)
        for lock in _stores:
            polomps.append({
                'id': lock.id,
                'serial': lock.serial,
                'status': lock.statusstore.name,
            })

        return JsonResponse({'message': msg, 'polomps': polomps, 'serial': str(serial), 'status': int(status), 'st': st,
                             'ticket': data['val']})


class BrandInCert(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)

        val = data['certid']
        _cbrand = CBrand.objects.filter(certificate_type_id=val)
        for cbrand in _cbrand:
            dict = {
                'id': cbrand.id,
                'name': cbrand.name
            }
            _list.append(dict)

        return JsonResponse({'message': 'success', 'mylist': _list,})


class QrTimeList(BaseAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        _list = []
        data = self.get_data(request.POST)

        val = data['gsid']
        _result = SellTime.objects.filter(gs_id=val).order_by('-id')
        for result in _result:
            dict = {
                'id': result.id,
                'name': str(result.date_in_jalali) +" - "+ str(result.date_out_jalali)
            }
            _list.append(dict)

        return JsonResponse({'message': 'success', 'mylist': _list,})