from django.db.models import Sum, Count, Q, Case, When
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from base.views import zoneorarea
from base.models import Ticket, Pump, Owner, Area, GsModel, Zone
from pay.models import StoreList, Store
from sell.models import SellGs, SellModel, IpcLog, Mojodi
from django.http import JsonResponse
from operator import itemgetter
from datetime import datetime, timedelta
import datetime
import jdatetime
import redis
from django.conf import settings
import logging
from django.core.cache import cache
from django.utils import timezone
from rest_framework.response import Response

# تنظیمات logging
logger = logging.getLogger(__name__)


# تابع کمکی برای محاسبه تاریخ
def get_date_range(days):
    today = datetime.date.today()
    return today - timedelta(days=days)


# تابع کمکی برای ساخت پاسخ JSON
def create_response(data, status=200):
    return JsonResponse(data, status=status)


def handle_error(message, status=400):
    logger.error(message)
    return create_response({'error': message}, status=status)


class SellSumView(APIView):

    def get(self, request, id):
        try:
            if id not in [1, 2, 3]:
                return handle_error('Invalid product ID', 400)
            product_map = {1: 2, 2: 3, 3: 4}
            _product = product_map.get(id)
            if not _product:
                return handle_error('Invalid product ID', 400)
            sell = SellGs.object_role.c_gs(request, 0).filter(product_id=_product)
            sell = sell.values('tarikh').annotate(
                amount=Sum('yarane') + Sum('nimeyarane') + Sum('ezterari') + Sum('azad1')).order_by(
                '-tarikh')[:30]
            sumamount = 0
            mylist = []
            for i in sell:
                sumamount += i['amount']
                mylist.append({
                    'tarikh': i['tarikh'].strftime('%Y/%m/%d'),
                    'amount': int(i['amount']),
                })
            mylist = sorted(mylist, key=itemgetter('tarikh'), reverse=False)
            return JsonResponse({'mylist': mylist, 'sumamount': sumamount / 30})

        except Exception as e:
            return handle_error(str(e), 500)


class SellNerkhView(APIView):

    def get(self, request, id):
        try:
            if id not in [4, 5]:
                return handle_error('Invalid product ID', 400)
            product_map = {4: 2, 5: 4}
            _product = product_map.get(id)
            if not _product:
                return handle_error('Invalid product ID', 400)

            sell = SellGs.object_role.c_gs(request, 0).filter(product_id=_product)
            sell = sell.values('tarikh').annotate(
                yarane=Sum('yarane'),
                nimeyarane=Sum('nimeyarane'),
                ezterari=Sum('ezterari'),
                azad=Sum('azad1')
            ).order_by('-tarikh')[:30]

            mylist = []
            for i in sell:
                print(i)
                mylist.append({
                    'tarikh': i['tarikh'].strftime('%Y/%m/%d'),
                    'yarane': i['yarane'],
                    'nimeyarane': (i['nimeyarane']),
                    'ezterari': (i['ezterari']),
                    'azad': (i['azad']),
                })

            mylist = sorted(mylist, key=itemgetter('tarikh'), reverse=False)
            return create_response({'mylist': mylist})

        except Exception as e:
            return handle_error(str(e), 500)


class SellCartView(APIView):

    def get(self, request, id):
        mylist = []
        if id not in [6, 7]:
            return handle_error('Invalid product ID', 400)
        product_map = {6: 2, 7: 4}
        _product = product_map.get(id)
        if not _product:
            return handle_error('Invalid product ID', 400)

        sell = SellGs.object_role.c_gs(request, 0).filter(product_id=_product)
        sell = sell.values('tarikh').annotate(yarane1=((Sum('yarane') + Sum('nimeyarane') +
                                                        Sum('azad1')) / (Sum('yarane') + Sum('nimeyarane') +
                                                                         Sum('azad1') + Sum('ezterari')) * 100),
                                              azad1=(Sum('ezterari') / (
                                                      Sum('yarane') + Sum('nimeyarane') +
                                                      Sum('azad1') + Sum('ezterari')) * 100)).order_by(
            '-tarikh')[:30]
        for i in sell:
            yarane = int(i['yarane1']) if i['yarane1'] else 0
            azad1 = int(i['azad1']) if i['azad1'] else 0
            dict = {
                'tarikh': i['tarikh'].strftime('%Y/%m/%d'),
                'yarane': yarane,
                'azad': azad1,
            }
            mylist.append(dict)
            mylist = sorted(mylist, key=itemgetter('tarikh'), reverse=False)

        return JsonResponse({'mylist': mylist})


class TicketsView(APIView):

    def get(self, request, id):
        try:
            status_map = {1: ([1010, 1011], [1, 2]), 2: ([1010], [1]), 3: ([1011], [2])}
            st, _st = status_map.get(id, ([], []))
            if not st or not _st:
                return handle_error('Invalid status ID', 400)

            listmasterticket = Ticket.objects.values('gs__area__zone__name', 'gs__area__zone_id').filter(
                failure__failurecategory_id__in=st, status__status='open'
            ).annotate(m=Count('id')).order_by('-m')[:37]

            listzone = []
            for item in listmasterticket:
                storecount = StoreList.objects.filter(
                    zone_id=item['gs__area__zone_id'],
                    statusstore_id__in=_st,
                    status_id__in=[3, 4]
                ).count()

                listzone.append({
                    'area': str(item['gs__area__zone__name']),
                    'listMasterTicket': item['m'],
                    'storecount': storecount,
                })

            return create_response({'mylist': listzone})

        except Exception as e:
            return handle_error(str(e), 500)


class NesbatView(APIView):

    def get(self, request, id):
        tedad = name = None
        bestzone = None
        bedzone = None
        myzone = None
        listzone = []
        listmasterticket = None
        _id = i = 0
        storecount = 0
        if id == 1:
            st = [1010, 1011]
            _st = [4, 3]

        zones = Zone.objects_limit.all()
        if request.user.owner.role.role in 'zone,setad,mgr':
            listmasterticket = Ticket.objects.values('gs__area__zone__name', 'gs__area__zone_id').filter(
                failure__failurecategory_id__in=[1010, 1011], status__status='open',
            ).annotate(m=Count('id')).order_by('-m')[:37]
        elif request.user.owner.role.role == 'area':
            listmasterticket = Ticket.objects.values('gs__area__name', 'gs__area_id').filter(
                failure__failurecategory_id__in=[1010, 1011], status__status='open',
            ).annotate(m=Count('id')).order_by('-m')[:37]
        zonelist = []
        for item in listmasterticket:
            if request.user.owner.role.role in 'zone,setad,mgr':
                storecount = Pump.objects.filter(gs__area__zone_id=item['gs__area__zone_id'],
                                                 status__status=True).count()
                name = str(item['gs__area__zone__name'])
                _id = str(item['gs__area__zone_id'])
            elif request.user.owner.role.role == 'area':
                storecount = Pump.objects.filter(gs__area_id=item['gs__area_id'],
                                                 status__status=True).count()
                name = str(item['gs__area__name'])
                _id = str(item['gs__area_id'])

            dictarea = {
                'area': name,
                'listMasterTicket': round((int(item['m']) / storecount) * 100, 2),
                'counter': item['m']
            }
            zonelist.append(str(_id))
            listzone.append(dictarea)
            listzone = sorted(listzone, key=itemgetter('listMasterTicket'), reverse=True)
            i = 1
            for item in listzone:
                if i == 1:
                    bedzone = item['area']
                if item['area'] == request.user.owner.zone.name and request.user.owner.role.role == 'zone':
                    myzone = i
                    tedad = item['counter']

                if item['area'] == request.user.owner.area.name and request.user.owner.role.role == 'area':
                    myzone = i
                    tedad = item['counter']

                bestzone = str(item['area']) + ' با رتبه :' + str(i) + '  (' + str(item['counter']) + 'خرابی)'
                i += 1

        if i == 37:
            for _zone in zones:
                if str(_zone.id) in zonelist:
                    pass
                else:
                    bestzone = str(_zone.name) + ' با رتبه :' + str(i) + '  (' + str(0) + 'خرابی)'

        return JsonResponse(
            {'mylist': listzone, 'bestzone': bestzone, 'bedzone': bedzone, 'myzone': myzone, 'tedad': tedad})


class Moghayerat(APIView):

    def get(self, request):
        try:
            rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                             password=settings.REDIS_PASS)
            formpermmision = rd.hgetall('moghayerat')
            listzone = []
            bestzone = bedzone = myzone = tedad = info = 0

            if formpermmision:
                for key, value in formpermmision.items():
                    _split = value.decode('utf-8').split('%')
                    info = _split[3]
                    listzone.append({
                        'area': _split[0],
                        'amount': int(_split[1]),
                        'moghayerat': float(_split[2]),
                    })
                listzone = sorted(listzone, key=itemgetter('moghayerat'), reverse=False)
                i = 1
                for item in listzone:
                    if i == 1:
                        bestzone = str(item['area']) + ' با رتبه :' + str(i)

                    if (item['area'] == request.user.owner.zone.name and request.user.owner.role.role == 'zone') or \
                            (item['area'] == request.user.owner.area.name and request.user.owner.role.role == 'area'):
                        myzone = i
                        tedad = item['amount']
                    bedzone = item['area']

                    i += 1

            return JsonResponse(
                {'bestzone': bestzone, 'bedzone': bedzone, 'myzone': myzone, 'tedad': tedad, 'info': info})
        except Exception as e:
            return handle_error(str(e), 500)


class CardShakhsi(APIView):

    def get(self, request):
        try:
            # ۱. کاهش بازه زمانی از ۶۰۰ روز به ۳۰ روز
            days_back = 30  # به جای ۶۰۰!
            date_from = datetime.datetime.today() - datetime.timedelta(days=days_back)

            # ۲. استفاده از کش
            cache_key = f"card_shakhsi_{request.user.owner.role.role}_{request.user.owner.zone.id}_{request.user.owner.refrence.id}"
            cached_result = cache.get(cache_key)

            if cached_result:
                return create_response(cached_result)

            # ۳. کوئری بهینه‌شده
            if request.user.owner.role.role == 'zone':
                zone_id = request.user.owner.zone_id
                results = SellGs.objects.filter(
                    tarikh__gte=date_from,
                    product_id=2,
                    gs__area__zone__iscoding=False
                ).values('gs__area__zone__name').annotate(
                    total_yarane=Sum('yarane'),
                    total_nimeyarane=Sum('nimeyarane'),
                    total_azad=Sum('azad1'),
                    total_ezterari=Sum('ezterari')
                )

            elif request.user.owner.role.role == 'area':
                area_id = request.user.owner.area_id
                results = SellGs.objects.filter(
                    tarikh__gte=date_from,
                    product_id=2,
                    gs__area__zone__iscoding=False
                ).values('gs__area__name').annotate(
                    total_yarane=Sum('yarane'),
                    total_nimeyarane=Sum('nimeyarane'),
                    total_azad=Sum('azad1'),
                    total_ezterari=Sum('ezterari')
                )
            else:
                return create_response({'error': 'دسترسی غیرمجاز'}, 403)

            # ۴. محاسبات در پایتون (سریع‌تر)
            listzone = []
            for item in results:
                name = item['gs__area__zone__name'] if 'gs__area__zone__name' in item else item['gs__area__name']
                total_yarane = item['total_yarane'] or 0
                total_nimeyarane = item['total_nimeyarane'] or 0
                total_azad = item['total_azad'] or 0
                total_ezterari = item['total_ezterari'] or 0

                total_n1_n2 = total_yarane + total_azad + total_nimeyarane
                total_all = total_n1_n2 + total_ezterari

                amount = (total_n1_n2 / total_all * 100) if total_all > 0 else 0

                listzone.append({
                    'area': name,
                    'amount': round(amount)
                })

            listzones = sorted(listzone, key=itemgetter('amount'), reverse=True)

            # ۶. پیدا کردن بهترین و بدترین
            bestzone = None
            bedzone = None
            myzone = None
            tedad = 0

            if listzones:
                bestzone = f"{listzones[0]['area']} با رتبه: ۱ ({listzones[0]['amount']}%)"
                bedzone = listzones[-1]['area']

                # پیدا کردن zone کاربر
                user_zone_name = request.user.owner.zone.name if request.user.owner.role.role == 'zone' else request.user.owner.area.name
                i = 0
                for zone_data in listzones:
                    i += 1
                    if zone_data['area'] == user_zone_name:
                        myzone = i
                        tedad = zone_data['amount']
                        break

            result = {
                'bestzone': bestzone,
                'bedzone': bedzone,
                'myzone': myzone,
                'tedad': tedad
            }

            cache.set(cache_key, result, 2000)

            return create_response(result)

        except Exception as e:
            print(e)
            return handle_error(str(e), 500)


class TekListView(APIView):

    def get(self, request):
        try:
            listowner = []

            for area in Owner.object_role.c_base(request).filter(role__role='tek', active=True):
                listmasterticket = Ticket.object_role.c_gs(request, 0).filter(failure__failurecategory_id=1010,
                                                                              status__status='open',
                                                                              gs__gsowner__owner_id=area.id).count()
                listpinpadticket = Ticket.object_role.c_gs(request, 0).filter(failure__failurecategory_id=1011,
                                                                              status__status='open',
                                                                              gs__gsowner__owner_id=area.id).count()
                listotherticket = Ticket.object_role.c_gs(request, 0).filter(
                    ~Q(failure__failurecategory_id__in=[1010, 1011]),
                    status__status='open',
                    gs__gsowner__owner_id=area.id).count()
                listowner.append({
                    'area': f"{area.name} {area.lname}",
                    'listMasterTicket': listmasterticket,
                    'listPinpadTicket': listpinpadticket,
                    'listOtherTicket': listotherticket,
                    'sum': int(listmasterticket) + int(listpinpadticket) + int(listotherticket),
                })
                listowner = sorted(listowner, key=itemgetter('sum'), reverse=True)

            return create_response({'mylist': listowner})
        except Exception as e:
            return handle_error(str(e), 500)


class NahyeListView(APIView):

    def get(self, request):
        listarea = []
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        for area in Area.object_role.c_base(request):
            listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
                                                     gs__area_id=area.id).count()
            listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
                                                     gs__area_id=area.id).count()
            listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
                                                    status__status='open',
                                                    gs__area_id=area.id).count()
            dictarea = {
                'area': str(area.name),
                'listMasterTicket': listmasterticket,
                'listPinpadTicket': listpinpadticket,
                'listOtherTicket': listotherticket,
                'sum': int(listmasterticket) + int(listpinpadticket) + int(listotherticket),
            }
            listarea.append(dictarea)

        listarea = sorted(listarea, key=itemgetter('sum'), reverse=True)
        # listarea = listarea[:10]
        return JsonResponse({'mylist': listarea})


class GSListView(APIView):

    def get(self, request):
        listgs = []
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        for area in GsModel.object_role.c_gsmodel(request):
            listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
                                                     gs_id=area.id).count()
            listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
                                                     gs_id=area.id).count()
            listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
                                                    status__status='open',
                                                    gs_id=area.id).count()
            dictarea = {
                'area': str(area.name) + ' ' + str(area.gsid),
                'listMasterTicket': listmasterticket,
                'listPinpadTicket': listpinpadticket,
                'listOtherTicket': listotherticket,
                'sum': int(listmasterticket) + int(listpinpadticket) + int(listotherticket),
            }
            listgs.append(dictarea)
        listgs = sorted(listgs, key=itemgetter('sum'), reverse=True)
        listgs = listgs[:10]
        return JsonResponse({'mylist': listgs})


class Ipclog_list_View(APIView):
    def get(self, request):
        ipclogs = None
        ipclist = []
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        ipclogs = IpcLog.object_role.c_gs(request, 0).aggregate(
            ck_rpm_version=(Count(Case(When(ck_rpm_version=False, then=1)))),
            ck_dashboard_version=(
                Count(Case(When(ck_dashboard_version=False, then=1)))),
            ck_pt_version=(Count(Case(When(ck_pt_version=False, then=1)))),
            ck_pt_online=(Count(Case(When(ck_pt_online=False, then=1)))),
            ck_quta_table_version=(
                Count(Case(When(ck_quta_table_version=False, then=1)))),
            ck_price_table_version=(
                Count(Case(When(ck_price_table_version=False, then=1)))),
            ck_zone_table_version=(
                Count(Case(When(ck_zone_table_version=False, then=1)))),
            ck_blacklist_version=(
                Count(Case(When(ck_blacklist_version=False, then=1)))),
            ck_blacklist_count=(Count(Case(When(ck_blacklist_count=False, then=1)))),

        )

        ipcdict = {
            'name': 'نگارش RPM',
            'tedad': ipclogs['ck_rpm_version']
        }
        if ipclogs['ck_rpm_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش GDS',
            'tedad': ipclogs['ck_dashboard_version']
        }
        if ipclogs['ck_dashboard_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش PT',
            'tedad': ipclogs['ck_pt_version']
        }
        if ipclogs['ck_pt_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'مغایرت نسخه PT آنلاین',
            'tedad': ipclogs['ck_pt_online']
        }
        if ipclogs['ck_pt_online'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش جدول سهمیه',
            'tedad': ipclogs['ck_quta_table_version']
        }
        if ipclogs['ck_quta_table_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش جدول قیمت',
            'tedad': ipclogs['ck_price_table_version']
        }
        if ipclogs['ck_price_table_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش جدول منطقه ایی',
            'tedad': ipclogs['ck_zone_table_version']
        }
        if ipclogs['ck_zone_table_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'نگارش لیست سیاه',
            'tedad': ipclogs['ck_blacklist_version']
        }
        if ipclogs['ck_blacklist_version'] > 0:
            ipclist.append(ipcdict)
        ipcdict = {
            'name': 'مغایرت تعداد بلک لیست',
            'tedad': ipclogs['ck_blacklist_count']
        }
        if ipclogs['ck_blacklist_count'] > 0:
            ipclist.append(ipcdict)

        return JsonResponse({'mylist': ipclist})


class TicketHourView(APIView):

    def get(self, request):
        list1 = []
        list2 = []
        list3 = []

        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)

        i = 15
        for item in range(16):
            tarikh = jdatetime.date.today() - jdatetime.timedelta(days=i)
            _year = tarikh.year
            _month = tarikh.month if len(str(tarikh.month)) == 2 else "0" + str(tarikh.month)
            _day = tarikh.day if len(str(tarikh.day)) == 2 else "0" + str(tarikh.day)

            store = Store.objects.filter(zone_id=request.user.owner.zone_id,
                                         resid_year=_year, resid_month=_month, resid_day=_day,
                                         status_id=3).aggregate(stores=Sum('master') + Sum('pinpad'))

            _store = store['stores'] if store['stores'] else 0

            tedad = (Ticket.object_role.c_gs(request, 0)
                     .filter(shamsi_date=datetime.date.today() - datetime.timedelta(days=i))).count()

            tedad2 = (Ticket.object_role.c_gs(request, 0)
                      .filter(status_id=2,
                              close_shamsi_date=datetime.date.today() - datetime.timedelta(days=i))).count()
            i -= 1

            tickets = {
                'tarikh': str(tarikh),
                'tedad': str(tedad),
                'tedad2': str(tedad2),
                'store': str(_store),

            }
            list1.append(tickets)

        listgs = sorted(list1, key=itemgetter('tarikh'), reverse=False)
        return JsonResponse({'mylist': listgs})


class AverageTicketsView(APIView):

    def get(self, request):
        list1 = []
        list2 = []
        list3 = []

        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)

        tarikh = jdatetime.date.today()
        tarikhen = datetime.date.today()

        _monthint = tarikh.month
        _monthinten = tarikhen.month

        _year = tarikh.year
        _yearen = tarikhen.year
        i = 0
        for item in range(12):
            i += 1
            _month = _monthint if len(str(_monthint)) == 2 else "0" + str(_monthint)
            _monthen = _monthinten if len(str(_monthinten)) == 2 else "0" + str(_monthinten)
            store = Store.objects.filter(zone_id=request.user.owner.zone_id,
                                         resid_year=_year, resid_month=_month,
                                         status_id=3).aggregate(stores=Sum('master') + Sum('pinpad'))

            _m = 31 if _month in ['01', '02', '03', '04', '05', '06'] else 30
            _men = 31 if _monthen in ['01', '03', '05', '07', '08', '10', '12'] else 30
            _store = store['stores'] if store['stores'] else 0
            _store = _store / _m
            tedad = Ticket.object_role.c_gs(request, 0).filter(shamsi_date__year=_yearen,
                                                               shamsi_date__month=_monthen).count()
            tedad = tedad / _men
            tedad2 = Ticket.object_role.c_gs(request, 0).filter(close_shamsi_date__year=_yearen,
                                                                close_shamsi_date__month=_monthen,
                                                                status_id=2).count()
            tedad2 = tedad2 / _men
            tedad = round(tedad, 1)
            tedad2 = round(tedad2, 1)
            _store = round(_store, 1)
            _date = str(_year) + "/" + str(_monthint)
            if _monthint == 1:
                _year = _year - 1
                _monthint = 12
            else:
                _monthint -= 1
            if _monthinten == 1:
                _yearen = _yearen - 1
                _monthinten = 12
            else:
                _monthinten -= 1

            tickets = {
                'tarikh': str(_date),
                'tedad': str(tedad),
                'tedad2': str(tedad2),
                'store': str(_store),
                'sort': i,

            }
            list1.append(tickets)

        listgs = sorted(list1, key=itemgetter('sort'), reverse=True)
        return JsonResponse({'mylist': listgs})


class SumTicketsMountView(APIView):

    def get(self, request):
        try:
            # ۱. محاسبه ۱۲ ماه گذشته در یک مرحله
            today = timezone.now().date()
            months_data = []

            for i in range(12):
                # محاسبه تاریخ برای هر ماه
                target_date = today - timedelta(days=30 * i)
                jdate = jdatetime.date.fromgregorian(date=target_date)

                months_data.append({
                    'year': jdate.year,
                    'month': jdate.month,
                    'year_gregorian': target_date.year,
                    'month_gregorian': target_date.month,
                    'sort': 12 - i  # برای مرتب‌سازی نزولی
                })

            # ۲. فقط ۳ کوئری اصلی به جای ۳۶ کوئری!

            # کوئری برای Storeها
            store_years = [data['year'] for data in months_data]
            store_months = [data['month'] for data in months_data]

            stores_data = Store.objects.filter(
                zone_id=request.user.owner.zone_id,
                resid_year__in=store_years,
                resid_month__in=store_months,
                status_id=3
            ).values('resid_year', 'resid_month').annotate(
                total_store=Sum('master') + Sum('pinpad')
            )

            # تبدیل به دیکشنری برای دسترسی سریع
            stores_dict = {
                f"{item['resid_year']}_{item['resid_month']}": item['total_store'] or 0
                for item in stores_data
            }

            # کوئری برای Ticketهای باز
            ticket_open_data = Ticket.object_role.c_gs(request, 0).filter(
                shamsi_date__year__in=[data['year'] for data in months_data],
                shamsi_date__month__in=[data['month'] for data in months_data]
            ).values('shamsi_date__year', 'shamsi_date__month').annotate(
                count_open=Count('id')
            )

            ticket_open_dict = {
                f"{item['shamsi_date__year']}_{item['shamsi_date__month']}": item['count_open']
                for item in ticket_open_data
            }

            # کوئری برای Ticketهای بسته
            ticket_closed_data = Ticket.object_role.c_gs(request, 0).filter(
                close_shamsi_date__year__in=[data['year_gregorian'] for data in months_data],
                close_shamsi_date__month__in=[data['month_gregorian'] for data in months_data],
                status_id=2
            ).values('close_shamsi_date__year', 'close_shamsi_date__month').annotate(
                count_closed=Count('id')
            )

            ticket_closed_dict = {
                f"{item['close_shamsi_date__year']}_{item['close_shamsi_date__month']}": item['count_closed']
                for item in ticket_closed_data
            }

            # ۳. ساخت نتیجه نهایی
            result_list = []

            for month_info in months_data:
                key = f"{month_info['year']}_{month_info['month']}"
                key_gregorian = f"{month_info['year_gregorian']}_{month_info['month_gregorian']}"

                store_count = stores_dict.get(key, 0)
                ticket_open = ticket_open_dict.get(key, 0)
                ticket_closed = ticket_closed_dict.get(key_gregorian, 0)

                result_list.append({
                    'tarikh': f"{month_info['year']}/{month_info['month']:02d}",
                    'tedad': ticket_open,
                    'tedad2': ticket_closed,
                    'store': store_count,
                    'sort': month_info['sort']
                })

            # ۴. مرتب‌سازی بر اساس sort
            result_list.sort(key=lambda x: x['sort'], reverse=True)

            return JsonResponse({'mylist': result_list})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SellAllProductView(APIView):

    def get(self, request, id):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        mylist = []
        avg_benzin = 0
        avg_super = 0
        avg_gaz = 0
        old_benzin = 0
        old_super = 0
        old_gaz = 0

        tarikh = datetime.date.today() - datetime.timedelta(days=1)
        datesell = SellModel.object_role.c_gs(request, 0).filter(tarikh=tarikh).values('gs_id').annotate(
            sellsum=Sum('sell'),
            kolsum=Sum('sellkol'))
        gsmodel = GsModel.object_role.c_gsmodel(request).filter(status_id=1)
        nosell = gsmodel.exclude(
            id__in=datesell.filter(sellsum__gte=0, kolsum__gte=0).values('gs_id')).count()

        zarfyat = GsModel.object_role.c_gsmodel(request).all().aggregate(benzin=Sum('m_benzin'),
                                                                         super=Sum('m_super'),
                                                                         naftgaz=Sum('m_naftgaz'))
        mojodi = Mojodi.object_role.c_gs(request, 0).filter(tarikh=tarikh).aggregate(benzin=Sum('benzin'),
                                                                                     super=Sum('super'),
                                                                                     naftgaz=Sum('gaz'))

        _benzin = round((int(mojodi['benzin']) / int(zarfyat['benzin'])) * 100) if mojodi['benzin'] else 0
        _super = round((int(mojodi['super']) / int(zarfyat['super'])) * 100) if mojodi['super'] else 0
        _naftgaz = round((int(mojodi['naftgaz']) / int(zarfyat['naftgaz'])) * 100) if mojodi['naftgaz'] else 0

        ticket = Ticket.object_role.c_gs(request, 0).filter(failure__failurecategory_id__in=[1010, 1011, 1015],
                                                            status_id=1).count()
        sell = SellGs.object_role.c_gs(request, 0).filter(tarikh__lte=tarikh)
        sell = sell.values('tarikh').annotate(
            benzin=Sum(Case(When(product_id=2, then='yarane'))) + Sum(Case(When(product_id=2, then='azad1'))) + Sum(
                Case(When(product_id=2, then='ezterari'))) + Sum(Case(When(product_id=2, then='nimeyarane'))) +
                   Sum(Case(When(product_id=2, then='haveleh'))),
            super=Sum(Case(When(product_id=3, then='yarane'))) + Sum(Case(When(product_id=3, then='azad1'))) + Sum(
                Case(When(product_id=3, then='ezterari'))) + Sum(Case(When(product_id=3, then='haveleh'))),
            gaz=Sum(Case(When(product_id=4, then='yarane'))) + Sum(Case(When(product_id=4, then='nimeyarane'))) +
                Sum(Case(When(product_id=4, then='azad1'))) + Sum(
                Case(When(product_id=4, then='ezterari'))) + Sum(Case(When(product_id=4, then='haveleh'))),

        ).order_by(
            '-tarikh')[:10]

        oldsell = SellGs.object_role.c_gs(request, 0).filter(tarikh=tarikh).aggregate(
            benzin=Sum(Case(When(product_id=2, then='yarane'))) + Sum(Case(When(product_id=2, then='azad1'))) + Sum(
                Case(When(product_id=2, then='ezterari'))) + Sum(Case(When(product_id=2, then='nimeyarane'))) +
                   Sum(Case(When(product_id=2, then='haveleh'))),
            super=Sum(Case(When(product_id=3, then='yarane'))) + Sum(Case(When(product_id=3, then='azad1'))) + Sum(
                Case(When(product_id=3, then='ezterari'))) + Sum(Case(When(product_id=3, then='haveleh'))),
            gaz=Sum(Case(When(product_id=4, then='yarane'))) + Sum(Case(When(product_id=4, then='azad'))) + Sum(
                Case(When(product_id=4, then='ezterari'))) + Sum(Case(When(product_id=4, then='nimeyarane'))) +
                Sum(Case(When(product_id=4, then='haveleh'))),
        )

        old_benzin = oldsell['benzin'] if oldsell['benzin'] else 0
        old_super = oldsell['super'] if oldsell['super'] else 0
        old_gaz = oldsell['gaz'] if oldsell['gaz'] else 0

        for i in sell:
            isbenzin = int(i['benzin']) if i['benzin'] else 0
            issuper = int(i['super']) if i['super'] else 0
            isgaz = int(i['gaz']) if i['gaz'] else 0

            avg_benzin += int(isbenzin)
            avg_super += int(issuper)
            avg_gaz += int(isgaz)

            dict = {
                'tarikh': i['tarikh'].strftime('%Y/%m/%d'),

                'benzin': str(isbenzin),
                'super': str(issuper),
                'gaz': str(isgaz),
            }

            mylist.append(dict)
            mylist = sorted(mylist, key=itemgetter('tarikh'), reverse=False)
        if id == 1:
            avg_benzin = avg_benzin / 10
            avg_super = avg_super / 10
            avg_gaz = avg_gaz / 10
        else:
            avg_benzin = old_benzin
            avg_super = old_super
            avg_gaz = old_gaz
        return JsonResponse(
            {'benzin': _benzin, 'super': _super, 'naftgaz': _naftgaz, 'mylist': mylist, 'avg_benzin': round(avg_benzin),
             'avg_super': round(avg_super), 'avg_gaz': round(avg_gaz), 'ticket': ticket, 'nosell': nosell})


class TamirKargahView(APIView):

    def get(self, request):
        list1 = []
        list2 = []
        list3 = []

        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)

        tarikh = jdatetime.date.today()
        tarikhen = datetime.date.today()

        _monthint = tarikh.month
        _monthinten = tarikhen.month

        _year = tarikh.year
        _yearen = tarikhen.year
        i = 0
        for item in range(12):
            i += 1
            _month = _monthint if len(str(_monthint)) == 2 else "0" + str(_monthint)
            _monthen = _monthinten if len(str(_monthinten)) == 2 else "0" + str(_monthinten)
            store = Store.objects.filter(zone_id=request.user.owner.zone_id,
                                         resid_year=_year, resid_month=_month,
                                         status_id=3).aggregate(stores=Sum('master') + Sum('pinpad'))

            _m = 31 if _month in ['01', '02', '03', '04', '05', '06'] else 30
            _men = 31 if _monthen in ['01', '03', '05', '07', '08', '10', '12'] else 30
            _store = store['stores'] if store['stores'] else 0
            _store = _store / _m
            tedad = Store.object_role.c_gs(request, 0).filter(marsole_date__year=_yearen,
                                                              marsole__month=_monthen).count()
            tedad = tedad / _men
            tedad2 = Ticket.object_role.c_gs(request, 0).filter(close_shamsi_date__year=_yearen,
                                                                close_shamsi_date__month=_monthen,
                                                                status_id=2).count()
            tedad2 = tedad2 / _men
            tedad = round(tedad, 1)
            tedad2 = round(tedad2, 1)
            _store = round(_store, 1)
            _date = str(_year) + "/" + str(_monthint)
            if _monthint == 1:
                _year = _year - 1
                _monthint = 12
            else:
                _monthint -= 1
            if _monthinten == 1:
                _yearen = _yearen - 1
                _monthinten = 12
            else:
                _monthinten -= 1

            tickets = {
                'tarikh': str(_date),
                'tedad': str(tedad),
                'tedad2': str(tedad2),
                'store': str(_store),
                'sort': i,

            }
            list1.append(tickets)

        listgs = sorted(list1, key=itemgetter('sort'), reverse=True)
        return JsonResponse({'mylist': listgs})


class ClearCacheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, _id):
        if _id == 1:
            cache_key = f"card_shakhsi_{request.user.owner.role.role}_{request.user.owner.zone.id}_{request.user.owner.refrence.id}"

        try:
            deleted = cache.delete(cache_key)
            if deleted:
                return Response({
                    'status': 'success',
                    'message': f'کش با کلید {cache_key} با موفقیت پاک شد'
                })
            else:
                return Response({
                    'status': 'warning',
                    'message': 'کش وجود نداشت یا قبلاً پاک شده بود'
                })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
