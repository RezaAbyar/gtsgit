import base64
import datetime
import hashlib
import zlib
from django.contrib.auth.models import User
from django.db.models import Sum, Count, When, Case
import json
from django.db.models import Prefetch
from accounts.models import Logs
from cart.models import CardAzad
from .models import IpcLog, IpcLogHistory, SellGs, CarInfo, Mojodi, ModemDisconnect, QRScan, SellTime, QrTime, \
    SellCardAzad, WaybillGs, DoreDate, Waybill
from base.models import Owner, GsModel, Pump, Ticket, Workflow, Parametrs, GsList, CloseGS
import jdatetime
from .models import SellModel
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
import re

today = str(jdatetime.date.today())

today = today.replace("-", "/")


def ticket_zone(_user, _id, zonever, zonegs):
    if zonever < zonegs and zonever != 0:
        ticket = Ticket.objects.filter(failure_id=1078, is_system=True, gs_id=_id, status_id=1)
        if ticket.count() == 0:
            a = Ticket.objects.create(owner_id=_user, status_id=1, organization_id=2, gs_id=_id,
                                      failure_id=1078, is_system=True)
            Workflow.objects.create(ticket_id=a.id, user_id=_user,
                                    description='این تیکت بر اساس مغایرت مشاهده شده در رمزینه بصورت سیستمی ایجاد شده است ',
                                    organization_id=2, failure_id=1078)
            return True
    return False


def autocloseticket(gsid, fid):
    user = User.objects.get(username='2161846736')
    tickets = Ticket.objects.filter(failure__enname=fid, gs__gsid=gsid, status_id=1)
    for ticket in tickets:
        ticket.status_id = 2
        ticket.actioner_id = user.owner.id
        ticket.descriptionactioner = 'تیکت بسته شد' + str('بستن سیستمی تیکت بعلت رفع خطا')
        ticket.close_shamsi_year = jdatetime.datetime.now().year
        if len(str(jdatetime.datetime.now().month)) == 1:
            month = '0' + str(jdatetime.datetime.now().month)
        else:
            month = jdatetime.datetime.now().month
        ticket.close_shamsi_month = month
        if len(str(jdatetime.datetime.now().day)) == 1:
            day = '0' + str(jdatetime.datetime.now().day)
        else:
            day = jdatetime.datetime.now().day
        ticket.close_shamsi_day = day
        ticket.closedate = datetime.datetime.now()
        ticket.close_shamsi_date = str(jdatetime.datetime.now().year) + "-" + str(month) + "-" + str(
            day)
        if ticket.closedate:
            try:
                ticket.timeaction = (ticket.closedate - ticket.create).days
            except:
                continue

            ticket.save()

        Workflow.objects.create(ticket_id=ticket.id, user_id=user.id,
                                description='بستن سیستمی تیکت بعلت رفع خطا',
                                organization_id=1, failure_id=ticket.failure_id)

    return True


def load_code(qr, id):
    inputcode = qr.split(":")
    a = inputcode[0]
    b = inputcode[1]
    if a == b:
        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)
        a = encrypt(id, 1, 1, 1, 1, 1, 1)
        return a
    else:
        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)
        print('please scan new code')


def qrtimeing(result, owner_id):
    """
    ثبت فروش ساعتی در مدل‌های SellTime و QrTime
    """

    try:
        # تبدیل رشته JSON به دیکشنری
        data_str = result[0] if isinstance(result, list) else result

        # تمیز کردن رشته و تبدیل به فرمت JSON معتبر
        # حذف کاراکترهای اضافی و escape
        data_str = data_str.strip()

        # اگر با ' شروع و پایان می‌یابد، آن را حذف کن
        if data_str.startswith("'") and data_str.endswith("'"):
            data_str = data_str[1:-1]

        # جایگزینی اسلش‌های escape شده
        data_str = data_str.replace("\\\\/", "/")

        # اضافه کردن آکولادهای جاافتاده
        if not data_str.startswith('{'):
            data_str = '{' + data_str
        if not data_str.endswith('}'):
            data_str = data_str + '}'

        gsid = data_str.split('"gs":')

        gs_id = gsid[1][:5].replace('"', '')
        qr_data = data_str.split('s":')
        qr_data_new = qr_data[1]
        qr_data_end = qr_data_new.split(',"d":')
        qr1 = qr_data_end[0]
        qr2 = qr_data_end[1]
        qr2 = qr2.replace(',"g', '')
        qr1 = json.loads(qr1)
        qr2 = json.loads(qr2)

        fd = qr1.get('fd', '')  # تاریخ شروع
        ed = qr1.get('ed', '')  # تاریخ پایان
        _yarane = 0
        _nimeyarane = 0
        # یافتن پمپ بنزین مربوطه
        try:
            gs = GsModel.objects.get(gsid=gs_id)
        except GsModel.DoesNotExist:

            print(f"پمپ بنزین با شناسه {gs_id} یافت نشد")
            return False

            # ایجاد یا به‌روزرسانی SellTime
        sell_time = SellTime.objects.create(datein=fd, dateout=ed, gs_id=gs.id, owner_id=owner_id,
                                            date_in_jalali=fd, date_out_jalali=ed)
        # پردازش داده‌های فروش ساعتی
        sales_data = qr2
        qr_time_objects = []

        for sale in sales_data:
            pump_number = sale.get('pt')  # شماره تلمبه
            fuel_type = sale.get('fu')  # نوع سوخت

            # تبدیل نوع سوخت به شناسه محصول
            product_id = 0
            if fuel_type == '01':
                product_id = 2  # بنزین
            elif fuel_type == '02':
                product_id = 3  # سوپر
            elif fuel_type == '03':
                product_id = 4  # گاز
            _n = 0
            if fuel_type == '01':
                _n = float(sale.get('a', 0))
                _yarane = float(sale.get('n', 0))
                _nimeyarane = float(sale.get('nn', 0))

            elif fuel_type == '02':
                _n = 0
                _yarane = 0
                _nimeyarane = 0
            elif fuel_type == '03':
                _n = float(sale.get('a', 0))
                _yarane = float(sale.get('n', 0))
                _nimeyarane = float(sale.get('nn', 0))

            # یافتن تلمبه مربوطه
            try:
                pump = Pump.objects.get(number=pump_number, gs=gs)

            except Pump.DoesNotExist:

                print(f"تلمبه با شماره {pump_number} برای پمپ بنزین {gs_id} یافت نشد")
                return False
            qr_time_objects.append(
                QrTime(
                    selltime=sell_time,
                    tolombeinfo_id=pump.id,
                    pumpnumber=pump_number,
                    yarane=_yarane,  # یارانه
                    nimeyarane=_nimeyarane,
                    azad1=_n,  # آزاد
                    azad=_n + _nimeyarane,
                    ezterari=float(sale.get('tKh', 0)),  # اضطراری
                    haveleh=0,  # در داده‌های نمونه وجود ندارد
                    azmayesh=float(sale.get('tK', 0))  # آزمایش
                )
            )

            # ایجاد تمام رکوردها به صورت bulk
        if qr_time_objects:
            QrTime.objects.bulk_create(qr_time_objects)

        # ایجاد یا به‌روزرسانی QrTime
        # QrTime.objects.create(
        #     selltime=sell_time,
        #     tolombeinfo_id=pump.id,
        #     pumpnumber=pump_number,
        #     yarane=_yarane,  # یارانه
        #     azad=_n,  # آزاد
        #     ezterari=float(sale.get('tKh', 0)),  # اضطراری
        #     haveleh=0,  # در داده‌های نمونه وجود ندارد
        #     azmayesh=float(sale.get('tK', 0))  # آزمایش
        # )

        return True

    except Exception as e:
        print(f"terr: {str(e)}")
        Logs.objects.create(
            parametr1=f'err: {str(e)}',
            parametr2=str(result),
            owner_id=owner_id
        )
        return False


def encrypt(id, st, ticket, userid, lat, long, failure):
    owner = Owner.objects.select_related('role', 'user').get(id=id)
    s = owner.qrcode
    ck_rpm_version = False
    ck_dashboard_version = False
    ck_pt_version = False
    ck_pt_online = True
    ck_quta_table_version = False
    ck_price_table_version = False
    ck_zone_table_version = False
    ck_blacklist_version = False
    ck_blacklist_count = False
    tarikh = datetime.date.today()
    Owner.del_qrcode(id=id)

    try:
        # print(s)
        data = str(zlib.decompress(base64.b64decode(s)))
        # print(data)

    except Exception as e:
        # print(e)
        Logs.objects.create(parametr1=f'{e}مشکل رمزنگاری در رمزینه ', parametr2=s, owner_id=owner.id)
        return redirect('sell:listsell')

    parametr = cache.get('system_parameters')
    if not parametr:
        parametr = Parametrs.objects.only(
            'dashboard_version', 'rpm_version', 'pt_version',
            'online_pt_version', 'quta_table_version',
            'price_table_version', 'blacklist_version',
            'autoticketbyqrcode', 'btmt'
        ).first()
        cache.set('system_parameters', parametr, 2000)  # 5 دقیقه کش

    owner.qrcode2 = data
    owner.save()
    data = owner.qrcode2
    data = data.replace('@@@@@@@@@@', '')
    try:
        _checkqr = data.split(']{"')

        if _checkqr[1][:1] == 's':
            qrtimeing(_checkqr[1:], id)
            return False
    except Exception as e:
        pass

    result = data.split("#")
    information = result[0].split(",")
    _jsoninfo = str(data.split("["))

    dore = information[1]

    if st != 2:
        if dore == "0" or dore[:1] == "-":
            Owner.del_qrcode(id=id)
            return 0
    gs_id = information[0][-4:]
    dashboard_version = information[4]
    try:
        isonlinegd = GsModel.objects.only(
            'id', 'gsid', 'isonline', 'zone_table_version',
            'iszonetable', 'isqrcode', 'addsell', 'area'
        ).select_related('area').get(gsid=gs_id)
    except GsModel.DoesNotExist:
        if st == 2:
            gs_id = Ticket.objects.get(id=ticket).gs.gsid
            isonlinegd = GsModel.objects.get(gsid=gs_id)
    except:
        if st == 2:
            gs_id = Ticket.objects.get(id=ticket).gs.gsid
            isonlinegd = GsModel.objects.get(gsid=gs_id)

    try:
        QRScan.objects.create(gs_id=isonlinegd.id, qr_data1=str(s), qr_data2=data, dore=dore, owner_id=owner.id)
    except Exception as e:
        print(e)
        pass

    try:
        _jsonmakhzan = result[0].split("[")
        if dashboard_version in ['1.04.020701', '1.04.021501']:
            ModemDisconnect.objects.filter(tarikh=tarikh, gs_id=isonlinegd.id).delete()
            disconnect = _jsonmakhzan[7].split("]")
            disconnect = disconnect[0]
            disconnect = '[' + disconnect + ']'
            data_list = json.loads(disconnect)
            disconnects_to_create = [
                ModemDisconnect(
                    gs_id=isonlinegd.id,
                    tarikh=tarikh,
                    starttime=item['ft'],
                    endtime=item['tt'],
                    ip=item['ip']
                )
                for item in data_list
                if item['ft'] != item['tt']
            ]
            ModemDisconnect.objects.bulk_create(disconnects_to_create)

        _jsonmakhzan = _jsonmakhzan[5].split("]")
        s = (_jsonmakhzan[0])

        s = s.replace("{", "").replace("}", "").split(",")
        dictionary = {}
        for i in s:
            dictionary[i.split(":")[0].strip('\'').replace("\"", "")] = i.split(":")[1].strip('"\'')

        benzin = 0
        _super = 0
        gaz = 0
        for m in s:
            rep = m.replace('"', '')
            _m = rep.split(":")
            if _m[0] == "01":
                benzin = _m[1]
            if _m[0] == "02":
                _super = _m[1]
            if _m[0] == "03":
                gaz = _m[1]
        pompcount = Pump.objects.filter(gs_id=isonlinegd.id).aggregate(
            pbenzin=Sum(Case(When(product_id=2, then=1), default=0)),
            psuper=Sum(Case(When(product_id=3, then=1), default=0)),
            pgaz=Sum(Case(When(product_id=4, then=1), default=0)),
        )

        if pompcount['pbenzin'] == 0:
            benzin = 0
        if pompcount['psuper'] == 0:
            _super = 0
        if pompcount['pgaz'] == 0:
            gaz = 0
        yesterday = tarikh - datetime.timedelta(days=1)
        # Mojodi.objects.filter(gs_id=isonlinegd.id, tarikh=yesterday).delete()

    except IndexError:
        pass

    try:
        Mojodi.objects.create(gs_id=isonlinegd.id, tarikh=yesterday, benzin=benzin, super=_super, gaz=gaz,
                              uniq=str(isonlinegd.id) + '-' + str(yesterday))
    except:
        pass
    if owner.role.role == 'gs':
        gslist = GsList.objects.select_related('owner', 'gs').filter(owner_id=owner.id, gs_id=isonlinegd.id).count()
        if gslist < 1:
            return redirect('sell:listsell')
    date_ipc = information[2]
    time_ipc = information[3]
    if dashboard_version in parametr.dashboard_version:
        ck_dashboard_version = True
    rpm_version = information[5]
    if rpm_version in parametr.rpm_version:
        if st == 2:
            result = Ticket.objects.get(id=int(ticket))
            if result.gs_id != isonlinegd.id:
                return redirect('sell:errorpage')
            result.closedate = datetime.datetime.now()
            result.status_id = 2
            result.save()
            Workflow.objects.create(ticket_id=int(ticket), organization_id=1, description='بستن تیکت RPM توسط تکنسین',
                                    user_id=userid, lat=lat, lang=long,
                                    failure_id=failure)

        ck_rpm_version = True
    # rpm_version = Encrypt(rpm_version)
    rpm_version_date = information[6]
    pt_version = information[7]
    if pt_version in parametr.pt_version:
        ck_pt_version = True

    if isonlinegd.isonline == True and parametr.online_pt_version != pt_version:
        ck_pt_online = False
    if isonlinegd.isonline == False:
        ck_pt_online = True
    if parametr.online_pt_version == pt_version:
        ck_pt_online = True

    if ck_pt_online and ck_blacklist_count and ck_blacklist_version and ck_pt_version and ck_rpm_version and ck_price_table_version and ck_dashboard_version and ck_quta_table_version and ck_zone_table_version:
        ck_contradiction = False
    else:
        ck_contradiction = True
    # pt_version = Encrypt(pt_version)

    quta_table_version = information[8]
    if quta_table_version in parametr.quta_table_version:
        ck_quta_table_version = True
    # quta_table_version = Encrypt(quta_table_version)
    xray = information[9].split("-")
    price_table_version = xray[0]
    if price_table_version in parametr.price_table_version:
        ck_price_table_version = True
    # price_table_version = Encrypt(price_table_version)
    zone_table_version = xray[1]
    if len(str(zone_table_version)) > 0:
        ck_zone_table_version = True
    if int(isonlinegd.zone_table_version) == 0:
        ck_zone_table_version = True
    if parametr.autoticketbyqrcode and isonlinegd.iszonetable:
        ticket_zone(owner.user.id, gs_id, zone_table_version, isonlinegd.zone_table_version)
    # zone_table_version = Encrypt(zone_table_version)
    blacklist_version = information[10]
    if parametr.blacklist_version <= blacklist_version:
        ck_blacklist_version = True
    # blacklist_version = Encrypt(blacklist_version)
    last_connection = information[11]
    # last_connection = Encrypt(last_connection)
    blacklist_count = information[12]

    if int(blacklist_count) <= int(settings.MAX_BLACKLIST_COUNT_ALERT) and int(blacklist_count) >= int(
            settings.MIN_BLACKLIST_COUNT_ALERT):
        ck_blacklist_count = True
        autocloseticket(gs_id, 'bllist')

    # blacklist_count = Encrypt(blacklist_count)

    hd_serial = information[13]
    os_version = information[14]
    # os_version = Encrypt(os_version)
    bl_ipc = information[15]
    connector = information[16]
    ismotabar = information[17][:1]
    imagever = information[18] if information[18] != 'Found' else '0'
    gs_version = information[19][:5]
    if dashboard_version in ['1.04.091601', '1.04.092502']:
        try:
            coding_count = information[23]
            modem_disconnrction = information[24].split(']')[0]
        except:
            coding_count = '0'
            modem_disconnrction = '0'

        try:
            hdd = information[20].split('-')
            hdd_total = hdd[0]
            hdd_empy = hdd[1]
            gs_version = information[19]
        except Exception as e:
            hdd_total = '0'
            hdd_empy = '0'

        try:
            ram_total = information[21]
        except:
            ram_total = '0'

        try:
            edr = int(information[22])
            edr = datetime.datetime.fromtimestamp(edr)
        except Exception as e:
            print(e)
            edr = '0'
    else:
        edr = '0'
        ram_total = '0'
        hdd_total = '0'
        hdd_empy = '0'
        coding_count = '0'
        modem_disconnrction = '0'

    gs = isonlinegd.id
    if dore != "0":
        year = dore[:4]
        month = dore[-6:]
        month = month[:2]
        day = dore[-4:]
        day = day[:2]
        tarikh = jdatetime.date(day=int(day), month=int(month), year=int(year)).togregorian()

    if dashboard_version in ['1.04.092502']:
        try:
            start_date = (information[25])
            end_date = (information[26].split(']')[0])
            DoreDate.objects.create(gs_id=gs, tarikh=tarikh, dore=dore, start_date=start_date, end_date=end_date)
        except:
            pass
    if len(connector) == 4:
        connector = "T" + str(connector)
    _connector = []

    _connector[:] = connector

    _modemname = _connector[0]
    _sam = True if _connector[4] == "1" else False
    _modem = True if _connector[1] == "1" else False
    _poler = True if _connector[3] == "1" else False
    _datacenter = True if _connector[2] == "1" else False
    if len(connector) > 6:
        _fasb = True if _connector[5] == "1" else False
        _as = True if _connector[6] == "1" else False
        _mellatmodem = True if _connector[7] == "1" else False
        _internet = True if _connector[8] == "1" else False
    else:
        _fasb = False
        _as = False
        _mellatmodem = False
        _internet = False
    try:
        IpcLog.objects.create(gsid=gs_id,
                              dore=dore,
                              gs_id=gs,
                              date_ipc=date_ipc,
                              time_ipc=time_ipc,
                              dashboard_version=dashboard_version,
                              rpm_version=rpm_version,
                              rpm_version_date=rpm_version_date,
                              pt_version=pt_version,
                              quta_table_version=quta_table_version,
                              price_table_version=price_table_version,
                              zone_table_version=zone_table_version,
                              blacklist_version=blacklist_version,
                              last_connection=last_connection,
                              blacklist_count=blacklist_count,
                              hd_serial=hd_serial,
                              os_version=os_version,
                              bl_ipc=bl_ipc,
                              modemname=_modemname,
                              sam=_sam,
                              modem=_modem,
                              poler=_poler,
                              fasb=_fasb,
                              asmelat=_as,
                              mellatmodem=_mellatmodem,
                              internet=_internet,
                              datacenter=_datacenter,
                              updatedate=datetime.datetime.now(),
                              uniq=str(gs),
                              ck_rpm_version=ck_rpm_version,
                              ck_dashboard_version=ck_dashboard_version,
                              ck_pt_version=ck_pt_version,
                              ck_pt_online=ck_pt_online,
                              ck_quta_table_version=ck_quta_table_version,
                              ck_price_table_version=ck_price_table_version,
                              ck_zone_table_version=ck_zone_table_version,
                              ck_blacklist_version=ck_blacklist_version,
                              ck_blacklist_count=ck_blacklist_count,
                              contradiction=ck_contradiction,
                              imagever=imagever,
                              gs_version=gs_version,
                              hdd_total=hdd_total,
                              hdd_empy=hdd_empy,
                              ram_total=ram_total,
                              edr=edr,
                              coding_count=coding_count,
                              modem_disconnrction=modem_disconnrction,

                              )
    except IntegrityError:
        update_ipclog = IpcLog.objects.get(gs_id=gs)
        update_ipclog.date_ipc = str(date_ipc)
        update_ipclog.time_ipc = str(time_ipc)
        update_ipclog.dashboard_version = str(dashboard_version)
        update_ipclog.rpm_version = str(rpm_version)
        update_ipclog.rpm_version_date = str(rpm_version_date)
        update_ipclog.pt_version = str(pt_version)
        update_ipclog.quta_table_version = str(quta_table_version)
        update_ipclog.price_table_version = str(price_table_version)
        update_ipclog.zone_table_version = str(zone_table_version)
        update_ipclog.blacklist_version = str(blacklist_version)
        update_ipclog.last_connection = str(last_connection)
        update_ipclog.blacklist_count = str(blacklist_count)
        update_ipclog.hd_serial = str(hd_serial)
        update_ipclog.os_version = str(os_version)
        update_ipclog.bl_ipc = str(bl_ipc)
        update_ipclog.modemname = str(_modemname)
        update_ipclog.sam = _sam
        update_ipclog.modem = _modem
        update_ipclog.poler = _poler
        update_ipclog.fasb = _fasb
        update_ipclog.asmelat = _as
        update_ipclog.mellatmodem = _mellatmodem
        update_ipclog.internet = _internet
        update_ipclog.datacenter = _datacenter
        update_ipclog.updatedate = str(datetime.datetime.now())
        update_ipclog.ck_rpm_version = ck_rpm_version
        update_ipclog.ck_dashboard_version = ck_dashboard_version
        update_ipclog.ck_pt_version = ck_pt_version
        update_ipclog.ck_pt_online = ck_pt_online
        update_ipclog.ck_quta_table_version = ck_quta_table_version
        update_ipclog.ck_price_table_version = ck_price_table_version
        update_ipclog.ck_zone_table_version = ck_zone_table_version
        update_ipclog.ck_blacklist_version = ck_blacklist_version
        update_ipclog.ck_blacklist_count = ck_blacklist_count
        update_ipclog.contradiction = ck_contradiction
        update_ipclog.imagever = imagever
        update_ipclog.gs_version = gs_version
        update_ipclog.hdd_total = hdd_total
        update_ipclog.hdd_empy = hdd_empy
        update_ipclog.ram_total = ram_total
        update_ipclog.edr = edr
        update_ipclog.coding_count = coding_count
        update_ipclog.modem_disconnrction = modem_disconnrction

        update_ipclog.save()
    try:
        IpcLogHistory.objects.create(gsid=gs_id,
                                     dore=dore,
                                     gs_id=gs,
                                     date_ipc=date_ipc,
                                     time_ipc=time_ipc,
                                     dashboard_version=dashboard_version,
                                     rpm_version=rpm_version,
                                     rpm_version_date=rpm_version_date,
                                     pt_version=pt_version,
                                     quta_table_version=quta_table_version,
                                     price_table_version=price_table_version,
                                     zone_table_version=zone_table_version,
                                     blacklist_version=blacklist_version,
                                     last_connection=last_connection,
                                     blacklist_count=blacklist_count,
                                     hd_serial=hd_serial,
                                     os_version=os_version,
                                     bl_ipc=bl_ipc,
                                     modemname=_modemname,
                                     sam=_sam,
                                     modem=_modem,
                                     poler=_poler,
                                     fasb=_fasb,
                                     asmelat=_as,
                                     mellatmodem=_mellatmodem,
                                     internet=_internet,
                                     datacenter=_datacenter,
                                     updatedate=datetime.datetime.now(),
                                     uniq=str(gs) + '-' + str(date_ipc),
                                     ck_rpm_version=ck_rpm_version,
                                     ck_dashboard_version=ck_dashboard_version,
                                     ck_pt_version=ck_pt_version,
                                     ck_pt_online=ck_pt_online,
                                     ck_quta_table_version=ck_quta_table_version,
                                     ck_price_table_version=ck_price_table_version,
                                     ck_zone_table_version=ck_zone_table_version,
                                     ck_blacklist_version=ck_blacklist_version,
                                     ck_blacklist_count=ck_blacklist_count,
                                     contradiction=ck_contradiction,
                                     imagever=imagever,
                                     gs_version=gs_version,
                                     hdd_total=hdd_total,
                                     hdd_empy=hdd_empy,
                                     ram_total=ram_total,
                                     edr=edr,
                                     coding_count=coding_count,
                                     modem_disconnrction=modem_disconnrction,

                                     )
    except IntegrityError:
        update_ipclog = IpcLogHistory.objects.get(date_ipc=date_ipc, gs_id=gs)
        update_ipclog.date_ipc = str(date_ipc)
        update_ipclog.time_ipc = str(time_ipc)
        update_ipclog.dashboard_version = str(dashboard_version)
        update_ipclog.rpm_version = str(rpm_version)
        update_ipclog.rpm_version_date = str(rpm_version_date)
        update_ipclog.pt_version = str(pt_version)
        update_ipclog.quta_table_version = str(quta_table_version)
        update_ipclog.price_table_version = str(price_table_version)
        update_ipclog.zone_table_version = str(zone_table_version)
        update_ipclog.blacklist_version = str(blacklist_version)
        update_ipclog.last_connection = str(last_connection)
        update_ipclog.blacklist_count = str(blacklist_count)
        update_ipclog.hd_serial = str(hd_serial)
        update_ipclog.os_version = str(os_version)
        update_ipclog.bl_ipc = str(bl_ipc)
        update_ipclog.modemname = str(_modemname)
        update_ipclog.sam = _sam
        update_ipclog.modem = _modem
        update_ipclog.poler = _poler
        update_ipclog.datacenter = _datacenter
        update_ipclog.fasb = _fasb
        update_ipclog.asmelat = _as
        update_ipclog.mellatmodem = _mellatmodem
        update_ipclog.internet = _internet
        update_ipclog.updatedate = str(datetime.datetime.now())
        update_ipclog.ck_rpm_version = ck_rpm_version
        update_ipclog.ck_dashboard_version = ck_dashboard_version
        update_ipclog.ck_pt_version = ck_pt_version
        update_ipclog.ck_pt_online = ck_pt_online
        update_ipclog.ck_quta_table_version = ck_quta_table_version
        update_ipclog.ck_price_table_version = ck_price_table_version
        update_ipclog.ck_zone_table_version = ck_zone_table_version
        update_ipclog.ck_blacklist_version = ck_blacklist_version
        update_ipclog.ck_blacklist_count = ck_blacklist_count
        update_ipclog.contradiction = ck_contradiction
        update_ipclog.imagever = imagever
        update_ipclog.gs_version = gs_version
        update_ipclog.hdd_total = hdd_total
        update_ipclog.hdd_empy = hdd_empy
        update_ipclog.ram_total = ram_total
        update_ipclog.edr = edr
        update_ipclog.coding_count = coding_count
        update_ipclog.modem_disconnrction = modem_disconnrction
        update_ipclog.save()

    if st == 2:
        return redirect('base:closeTicket')

    for ticket in Ticket.objects.filter(gs__gsid=gs_id, failure__autoclosebyqrcode=True, status_id=1):
        if rpm_version in parametr.rpm_version:
            user = User.objects.get(username='2161846736')
            ticket.status_id = 2
            ticket.actioner_id = user.owner.id
            ticket.descriptionactioner = 'تیکت بسته شد' + str('بستن تیکت با اسکن رمزینه')
            ticket.close_shamsi_year = jdatetime.datetime.now().year
            if len(str(jdatetime.datetime.now().month)) == 1:
                month = '0' + str(jdatetime.datetime.now().month)
            else:
                month = jdatetime.datetime.now().month
            ticket.close_shamsi_month = month
            if len(str(jdatetime.datetime.now().day)) == 1:
                day = '0' + str(jdatetime.datetime.now().day)
            else:
                day = jdatetime.datetime.now().day
            ticket.close_shamsi_day = day
            ticket.closedate = datetime.datetime.now()
            ticket.close_shamsi_date = str(jdatetime.datetime.now().year) + "-" + str(month) + "-" + str(
                day)
            if ticket.closedate:
                try:
                    ticket.timeaction = (ticket.closedate - ticket.create).days
                except:
                    continue

                ticket.save()

            Workflow.objects.create(ticket_id=ticket.id, user_id=user.id,
                                    description='بستن تیکت با اسکن رمزینه',
                                    organization_id=1, failure_id=ticket.failure_id)
    _today = datetime.date.today()
    olddate = _today - datetime.timedelta(days=10)

    if not isonlinegd.isqrcode:

        if ismotabar == "1" or tarikh < olddate or tarikh > _today:
            # OtherError.objects.created(info=f'ismotabar={ismotabar}-tarikh={tarikh}-olddate={olddate}-today={today}')
            Owner.del_qrcode(id=id)
            return data

    try:
        """درج کارت آزاد"""

        _azad = _jsoninfo.split("]#")
        _azad = _azad[0].split("', '")
        insert_card_azad(_azad[12], isonlinegd.id, tarikh)
    except:
        pass

    try:
        """بارنامه GS"""

        _waybill = _jsoninfo.split("]#")
        _waybill = _waybill[0].split("', '")
        insert_waybill_gs(_waybill[10], isonlinegd.id)

    except IndexError:
        pass

    try:
        """درج نوع کارت"""

        _jsoninfo = _jsoninfo.split("]#")
        _jsoninfo = _jsoninfo[0].split("', '")
        insert_card_info(_jsoninfo[3], isonlinegd.id, isonlinegd.gsid, tarikh)

    except IndexError:
        pass

    sell_objects_to_create = []
    sell_objects_to_update = []
    existing_uniqs = []
    for item in range(len(result)):
        nime = 0
        if item > 0 and dore != "0":
            sellitem = result[item].split(',')
            if dashboard_version == '1.02.101701':
                hvle = sellitem[7].replace("'", "")
                mindatecheck = "0"
            else:
                hvle = sellitem[7]
                mindatecheck = sellitem[8].replace("'", "")
            _product = 0

            if sellitem[1] == '01':
                _product = 2
            if sellitem[1] == '02':
                _product = 3
            if sellitem[1] == '03':
                _product = 4
            if sellitem[1] == '04':
                _product = 948

            if int(sellitem[0] == "0"):
                for nazel in Pump.objects.filter(status_id=1, gs_id=isonlinegd.id):
                    try:
                        SellModel.objects.create(gs_id=gs, tolombeinfo_id=nazel.id,
                                                 ezterari=0, pumpnumber=nazel.number,
                                                 tarikh=tarikh, yarane=0, nimeyarane=0, azad1=0, azad=0, haveleh=0,
                                                 azmayesh=0, dore=dore, sellkol=0, mindatecheck=mindatecheck,
                                                 uniq=str(tarikh) + "-" + str(gs) + "-" + str(nazel.id))
                    except IntegrityError:
                        Owner.del_qrcode(id=id)
                        return data
                Owner.del_qrcode(id=id)
                return data

            if int(sellitem[2]) > 0:
                yarane = int(sellitem[2]) / 100
            else:
                yarane = 0
            if int(sellitem[3]) > 0:
                nimeyarane = int(sellitem[3]) / 100
            else:
                nimeyarane = 0
            if int(sellitem[4]) > 0:
                azad1 = int(sellitem[4]) / 100
            else:
                azad1 = 0

            if int(sellitem[4]) > 0 or int(sellitem[3]) > 0:
                azad = (int(sellitem[4]) / 100)

                if _product == 2:
                    nime = (int(sellitem[3]) / 100)
                    azad = azad + nime

            else:
                azad = 0
            if int(sellitem[5]) > 0:
                ezterari = int(sellitem[5]) / 100
            else:
                ezterari = 0
            if int(hvle) > 0:
                haveleh = int(hvle) / 100
            else:
                haveleh = 0
            if int(sellitem[6]) > 0:
                azmayesh = int(sellitem[6]) / 100
            else:
                azmayesh = 0

            pomp = Pump.objects.get(number=int(sellitem[0]), gs_id=gs)
            if pomp.product_id != _product:
                pomp.product_id = _product
                pomp.save()

            if int(sellitem[2]) > 0:
                yarane = int(sellitem[2]) / 100
            else:
                yarane = 0

            uniq_value = str(tarikh) + "-" + str(gs) + "-" + str(pomp.id)
            try:
                existing_sell = SellModel.objects.get(uniq=uniq_value)
                # اگر وجود دارد، آپدیت می‌کنیم
                existing_sell.ezterari = ezterari
                existing_sell.product_id = _product
                existing_sell.yarane = yarane
                existing_sell.nimeyarane = nimeyarane
                existing_sell.azmayesh = azmayesh
                existing_sell.haveleh = haveleh
                existing_sell.azad1 = azad1
                existing_sell.azad = azad
                existing_sell.mindatecheck = mindatecheck
                existing_sell.sellkol = ezterari + azad1 + yarane + nimeyarane + azmayesh
                sell_objects_to_update.append(existing_sell)
                existing_uniqs.append(uniq_value)
            except SellModel.DoesNotExist:
                # اگر وجود ندارد، ایجاد می‌کنیم
                sell_objects_to_create.append(
                    SellModel(
                        gs_id=gs,
                        tolombeinfo_id=pomp.id,
                        product_id=_product,
                        ezterari=ezterari,
                        pumpnumber=pomp.number,
                        tarikh=tarikh,
                        yarane=yarane,
                        nimeyarane=nimeyarane,
                        azad=azad,
                        azad1=azad1,
                        haveleh=haveleh,
                        mindatecheck=mindatecheck,
                        azmayesh=azmayesh,
                        dore=dore,
                        sell=0,
                        sellkol=ezterari + azad1 + nimeyarane + yarane + azmayesh,
                        uniq=uniq_value
                    )
                )
    if isonlinegd.addsell and parametr.btmt:
        if sell_objects_to_create:
            SellModel.objects.bulk_create(sell_objects_to_create)
            # print(f"{len(sell_objects_to_create)} رکورد جدید SellModel ایجاد شد")

        if sell_objects_to_update:
            SellModel.objects.bulk_update(
                sell_objects_to_update,
                ['ezterari', 'product_id', 'yarane', 'nimeyarane', 'azad1', 'azmayesh', 'haveleh', 'azad',
                 'mindatecheck', 'sellkol']
            )
        # try:
        #     SellModel.objects.create(gs_id=gs, tolombeinfo_id=pomp.id, product_id=_product,
        #                              ezterari=ezterari, pumpnumber=pomp.number,
        #                              tarikh=tarikh, yarane=yarane, azad=azad, haveleh=haveleh,
        #                              mindatecheck=mindatecheck,
        #                              azmayesh=azmayesh, dore=dore, sellkol=ezterari + azad + yarane + azmayesh,
        #                              uniq=str(tarikh) + "-" + str(gs) + "-" + str(pomp.id))
        # except:
        #     sell = SellModel.objects.get(uniq=str(tarikh) + "-" + str(gs) + "-" + str(pomp.id))
        #     sell.ezterari = ezterari
        #     sell.product_id = _product
        #     sell.yarane = yarane
        #     sell.azmayesh = azmayesh
        #     sell.haveleh = haveleh
        #     sell.azad = azad
        #     sell.mindatecheck = mindatecheck
        #     sell.sellkol = ezterari + azad + yarane + azmayesh
        #     sell.save()

    if dore != "0":
        SellGs.sell_get_or_create(gs=gs, tarikh=tarikh)
    if isonlinegd.area.zone.iscloseticketissell:
        check_ticket_is_sell(gs)
    Owner.del_qrcode(id=id)
    return data


def load_rpm_code(userid, qr, id, ticket, lat, long, failure):
    inputcode = qr.split(":")
    a = inputcode[0]
    b = inputcode[1]
    if a == b:
        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)

        encrypt(id, 2, ticket, userid, lat, long, failure)
    else:
        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)
        print('please scan new code')


def checksell(_id):
    ck_rpm_version = False
    ck_dashboard_version = False
    ck_pt_version = False
    ck_pt_online = True
    ck_quta_table_version = False
    ck_price_table_version = False
    ck_zone_table_version = False
    ck_blacklist_version = False
    ck_blacklist_count = False
    ck_contradiction = False
    parametr = Parametrs.objects.all().first()
    data = Owner.objects.get(id=_id).qrcode2
    data = data.replace('@@@@@@@@@@', '')
    result = data.split("#")
    information = result[0].split(",")
    gsid = information[0][-4:]
    gs_id = gsid
    isonlinegd = GsModel.objects.get(gsid=gs_id)
    # gsid = Encrypt(gsid)
    dore = information[1]
    date_ipc = information[2]
    time_ipc = information[3]
    dashboard_version = information[4]
    if dashboard_version in parametr.dashboard_version:
        ck_dashboard_version = True
    rpm_version = information[5]
    if rpm_version in parametr.rpm_version:
        ck_rpm_version = True
    # rpm_version = Encrypt(rpm_version)
    rpm_version_date = information[6]
    pt_version = information[7]
    if pt_version in parametr.pt_version:
        ck_pt_version = True

    if isonlinegd.isonline == True and parametr.online_pt_version != pt_version:
        ck_pt_online = False
    if isonlinegd.isonline == False:
        ck_pt_online = True
    if parametr.online_pt_version == pt_version:
        ck_pt_online = True

    if ck_pt_online and ck_blacklist_count and ck_blacklist_version and ck_pt_version and ck_rpm_version and ck_price_table_version and ck_dashboard_version and ck_quta_table_version and ck_zone_table_version:
        ck_contradiction = False
    else:
        ck_contradiction = True
    # pt_version = Encrypt(pt_version)

    quta_table_version = information[8]
    if quta_table_version in parametr.quta_table_version:
        ck_quta_table_version = True
    # quta_table_version = Encrypt(quta_table_version)
    xray = information[9].split("-")
    price_table_version = xray[0]
    if price_table_version in parametr.price_table_version:
        ck_price_table_version = True
    # price_table_version = Encrypt(price_table_version)
    zone_table_version = xray[1]
    if len(zone_table_version) > 0 and zone_table_version >= isonlinegd.zone_table_version:
        ck_zone_table_version = True
    if int(isonlinegd.zone_table_version) == 0:
        ck_zone_table_version = True
    # ticket_zone(owner.user.id, gs_id, zone_table_version)
    # zone_table_version = Encrypt(zone_table_version)
    blacklist_version = information[10]
    if parametr.blacklist_version <= blacklist_version:
        ck_blacklist_version = True
    # blacklist_version = Encrypt(blacklist_version)
    last_connection = information[11]
    # last_connection = Encrypt(last_connection)
    blacklist_count = information[12]
    if int(blacklist_count) <= int(settings.MAX_BLACKLIST_COUNT_ALERT) and int(blacklist_count) >= int(
            settings.MIN_BLACKLIST_COUNT_ALERT):
        ck_blacklist_count = True
    # blacklist_count = Encrypt(blacklist_count)
    if dashboard_version == '1.02.101701':
        hd_serial = information[13]
        os_version = information[14]
        # os_version = Encrypt(os_version)
        bl_ipc = information[15][:-1]
        # bl_ipc = Encrypt(bl_ipc)
    else:
        hd_serial = information[13][:-1]
        os_version = '0'
        # os_version = Encrypt(os_version)
        bl_ipc = '0'
        # bl_ipc = Encrypt(bl_ipc)
    gs = isonlinegd.id
    if dore != "0":
        year = dore[:4]
        month = dore[-6:]
        month = month[:2]
        day = dore[-4:]
        day = day[:2]
        tarikh = jdatetime.date(day=int(day), month=int(month), year=int(year)).togregorian()

    try:
        IpcLog.objects.create(gsid=gsid,
                              dore=dore,
                              gs_id=gs,
                              date_ipc=date_ipc,
                              time_ipc=time_ipc,
                              dashboard_version=dashboard_version,
                              rpm_version=rpm_version,
                              rpm_version_date=rpm_version_date,
                              pt_version=pt_version,
                              quta_table_version=quta_table_version,
                              price_table_version=price_table_version,
                              zone_table_version=zone_table_version,
                              blacklist_version=blacklist_version,
                              last_connection=last_connection,
                              blacklist_count=blacklist_count,
                              hd_serial=hd_serial,
                              os_version=os_version,
                              bl_ipc=bl_ipc,
                              updatedate=datetime.datetime.now(),
                              uniq=str(gs),
                              ck_rpm_version=ck_rpm_version,
                              ck_dashboard_version=ck_dashboard_version,
                              ck_pt_version=ck_pt_version,
                              ck_pt_online=ck_pt_online,
                              ck_quta_table_version=ck_quta_table_version,
                              ck_price_table_version=ck_price_table_version,
                              ck_zone_table_version=ck_zone_table_version,
                              ck_blacklist_version=ck_blacklist_version,
                              ck_blacklist_count=ck_blacklist_count,
                              contradiction=ck_contradiction
                              )
    except IntegrityError:
        update_ipclog = IpcLog.objects.get(gs_id=gs)
        update_ipclog.date_ipc = str(date_ipc)
        update_ipclog.time_ipc = str(time_ipc)
        update_ipclog.dashboard_version = str(dashboard_version)
        update_ipclog.rpm_version = str(rpm_version)
        update_ipclog.rpm_version_date = str(rpm_version_date)
        update_ipclog.pt_version = str(pt_version)
        update_ipclog.quta_table_version = str(quta_table_version)
        update_ipclog.price_table_version = str(price_table_version)
        update_ipclog.zone_table_version = str(zone_table_version)
        update_ipclog.blacklist_version = str(blacklist_version)
        update_ipclog.last_connection = str(last_connection)
        update_ipclog.blacklist_count = str(blacklist_count)
        update_ipclog.hd_serial = str(hd_serial)
        update_ipclog.os_version = str(os_version)
        update_ipclog.bl_ipc = str(bl_ipc)
        update_ipclog.updatedate = str(datetime.datetime.now())
        update_ipclog.ck_rpm_version = ck_rpm_version
        update_ipclog.ck_dashboard_version = ck_dashboard_version
        update_ipclog.ck_pt_version = ck_pt_version
        update_ipclog.ck_pt_online = ck_pt_online
        update_ipclog.ck_quta_table_version = ck_quta_table_version
        update_ipclog.ck_price_table_version = ck_price_table_version
        update_ipclog.ck_zone_table_version = ck_zone_table_version
        update_ipclog.ck_blacklist_version = ck_blacklist_version
        update_ipclog.ck_blacklist_count = ck_blacklist_count
        update_ipclog.contradiction = ck_contradiction
        update_ipclog.save()
    try:
        IpcLogHistory.objects.create(gsid=gsid,
                                     dore=dore,
                                     gs_id=gs,
                                     date_ipc=date_ipc,
                                     time_ipc=time_ipc,
                                     dashboard_version=dashboard_version,
                                     rpm_version=rpm_version,
                                     rpm_version_date=rpm_version_date,
                                     pt_version=pt_version,
                                     quta_table_version=quta_table_version,
                                     price_table_version=price_table_version,
                                     zone_table_version=zone_table_version,
                                     blacklist_version=blacklist_version,
                                     last_connection=last_connection,
                                     blacklist_count=blacklist_count,
                                     hd_serial=hd_serial,
                                     os_version=os_version,
                                     bl_ipc=bl_ipc,
                                     updatedate=datetime.datetime.now(),
                                     uniq=str(gs) + '-' + str(date_ipc),
                                     ck_rpm_version=ck_rpm_version,
                                     ck_dashboard_version=ck_dashboard_version,
                                     ck_pt_version=ck_pt_version,
                                     ck_pt_online=ck_pt_online,
                                     ck_quta_table_version=ck_quta_table_version,
                                     ck_price_table_version=ck_price_table_version,
                                     ck_zone_table_version=ck_zone_table_version,
                                     ck_blacklist_version=ck_blacklist_version,
                                     ck_blacklist_count=ck_blacklist_count,
                                     contradiction=ck_contradiction
                                     )
    except IntegrityError:
        update_ipclog = IpcLogHistory.objects.get(date_ipc=date_ipc, gs_id=gs)
        update_ipclog.date_ipc = str(date_ipc)
        update_ipclog.time_ipc = str(time_ipc)
        update_ipclog.dashboard_version = str(dashboard_version)
        update_ipclog.rpm_version = str(rpm_version)
        update_ipclog.rpm_version_date = str(rpm_version_date)
        update_ipclog.pt_version = str(pt_version)
        update_ipclog.quta_table_version = str(quta_table_version)
        update_ipclog.price_table_version = str(price_table_version)
        update_ipclog.zone_table_version = str(zone_table_version)
        update_ipclog.blacklist_version = str(blacklist_version)
        update_ipclog.last_connection = str(last_connection)
        update_ipclog.blacklist_count = str(blacklist_count)
        update_ipclog.hd_serial = str(hd_serial)
        update_ipclog.os_version = str(os_version)
        update_ipclog.bl_ipc = str(bl_ipc)
        update_ipclog.updatedate = str(datetime.datetime.now())
        update_ipclog.ck_rpm_version = ck_rpm_version
        update_ipclog.ck_dashboard_version = ck_dashboard_version
        update_ipclog.ck_pt_version = ck_pt_version
        update_ipclog.ck_pt_online = ck_pt_online
        update_ipclog.ck_quta_table_version = ck_quta_table_version
        update_ipclog.ck_price_table_version = ck_price_table_version
        update_ipclog.ck_zone_table_version = ck_zone_table_version
        update_ipclog.ck_blacklist_version = ck_blacklist_version
        update_ipclog.ck_blacklist_count = ck_blacklist_count
        update_ipclog.contradiction = ck_contradiction
        update_ipclog.save()
    for item in range(len(result)):

        if item > 0:
            sellitem = result[item].split(',')
            hvle = sellitem[7].replace("'", "")
            _product = 0
            if sellitem[1] == '01':
                _product = 2
            if sellitem[1] == '02':
                _product = 3
            if sellitem[1] == '03':
                _product = 4
            if sellitem[1] == '04':
                _product = 948

            # print(sellitem[0])
            # print(int(sellitem[5]) / 100)
            if int(sellitem[2]) > 0:
                yarane = int(sellitem[2]) / 100
            else:
                yarane = 0
            if int(sellitem[4]) > 0:
                azad = int(sellitem[4]) / 100
            else:
                azad = 0
            if int(sellitem[5]) > 0:
                ezterari = int(sellitem[5]) / 100
            else:
                ezterari = 0
            if int(hvle) > 0:
                haveleh = int(hvle) / 100
            else:
                haveleh = 0
            if int(sellitem[6]) > 0:
                azmayesh = int(sellitem[6]) / 100
            else:
                azmayesh = 0

            pomp = Pump.objects.get(number=int(sellitem[0]), gs_id=gs)
            if pomp.product_id != _product:
                pomp.product_id = _product
                pomp.save()
            if _product == 2:
                if int(sellitem[2]) > 0:
                    yarane = int(sellitem[2]) / 100
                else:
                    yarane = 0
            elif _product == 4:
                if int(sellitem[3]) > 0:
                    yarane = int(sellitem[3]) / 100
                else:
                    yarane = 0
            try:
                SellModel.objects.create(gs_id=gs, tolombeinfo_id=pomp.id, product_id=_product,
                                         ezterari=ezterari, pumpnumber=pomp.number,
                                         tarikh=tarikh, yarane=yarane, azad=azad, haveleh=haveleh,
                                         azmayesh=azmayesh, dore=dore, sellkol=ezterari + azad + yarane + azmayesh,
                                         uniq=str(tarikh) + "-" + str(gs) + "-" + str(pomp.id))
            except:
                sell = SellModel.objects.get(uniq=str(tarikh) + "-" + str(gs) + "-" + str(pomp.id))
                sell.product_id = _product
                sell.ezterari = ezterari
                sell.yarane = yarane
                sell.azmayesh = azmayesh
                sell.haveleh = haveleh
                sell.azad = azad
                sell.sellkol = ezterari + azad + yarane + azmayesh
                sell.save()
    SellGs.sell_get_or_create(gs=gs, tarikh=tarikh)

    return data


def check_ticket_is_sell(gs):
    tickets = Ticket.objects.filter(status_id=1, gs_id=gs, failure__failurecategory_id__in=[1010, 1011])

    for ticket in tickets:
        sellmodel = SellModel.objects.exclude(sellkol=0).filter(tolombeinfo_id=ticket.Pump_id,
                                                                tarikh__gt=ticket.shamsi_date
                                                                ).aggregate(summ=Sum('sellkol'), tedad=Count('id'))

        if sellmodel['summ'] and int(sellmodel['summ']) > 700 and int(sellmodel['tedad']) > 2:
            ticket.descriptionactioner = 'تیکت بعلت اینکه نازل بیش از دو روز دارای فروش بوده ، بصورت سیستمی بسته شد'
            ticket.status_id = 2
            ticket.star = 5
            ticket.reply_id = 54
            ticket.actioner_id = 5825
            ticket.close_shamsi_year = jdatetime.datetime.now().year
            if len(str(jdatetime.datetime.now().month)) == 1:
                month = '0' + str(jdatetime.datetime.now().month)
            else:
                month = jdatetime.datetime.now().month
            ticket.close_shamsi_month = month
            if len(str(jdatetime.datetime.now().day)) == 1:
                day = '0' + str(jdatetime.datetime.now().day)
            else:
                day = jdatetime.datetime.now().day
            ticket.close_shamsi_day = day
            ticket.closedate = datetime.datetime.now()
            ticket.close_shamsi_date = str(jdatetime.datetime.now().year) + "-" + str(month) + "-" + str(day)
            ticket.save()
            Workflow.objects.create(ticket_id=ticket.id, user_id=1,
                                    description='تیکت بعلت اینکه نازل بیش از دو روز دارای فروش بوده ، بصورت سیستمی بسته شد',
                                    organization_id=1, failure_id=ticket.failure_id)


def insert_card_azad(result, gs, tarikh):
    """داده های کارت آزاد جایگاه"""

    try:
        SellCardAzad.objects.filter(gs_id=gs, tarikh=tarikh).delete()
        result = result.replace(']', '')
        cards_data = result.strip().split('","')

        cards_to_create = []

        for card_data in cards_data:
            # حذف کوتیشن‌ها از ابتدا و انتها
            card_data = card_data.replace('"', '').strip()

            # تقسیم بخش‌های کارت
            parts = card_data.split('-')

            if len(parts) == 4:
                card_number = parts[0]

                try:
                    sale_amount = float(parts[1]) if '.' in parts[1] else int(parts[1])
                    count = int(parts[2])
                    product = int(parts[3])
                    product = 2 if product == 1 else 4

                    cards_to_create.append(SellCardAzad(
                        card_number=card_number,
                        sale_amount=sale_amount,
                        count=count,
                        tarikh=tarikh,
                        gs_id=gs,
                        product_id=product
                    ))
                except ValueError:
                    # اگر داده‌ها معتبر نباشند
                    continue

        # ذخیره همه کارت‌ها در یک تراکنش
        if cards_to_create:
            SellCardAzad.objects.bulk_create(cards_to_create)

        return len(cards_to_create)
    except:
        pass


def insert_card_info(result, gs, gsid, tarikh):
    """درج نوع کارت"""
    try:
        cardict = result
        cardict = cardict.replace("'", "")
        cardict = cardict.replace("]", "")
        cardict = cardict.replace('"', "")
        cardict = cardict.replace(' ', "")
        cardict = cardict.split(",")
        i = 0
        _newlist = []

        for car in cardict:

            if i != -1:
                if ":" in car:
                    ca = car.split(":")
                    car = ca[1]

                car = car.replace('}', "")
                car = car.replace('{', "")

                dict = {
                    'key': i + 1,
                    'value': car
                }
                _newlist.append(dict)
            i += 1

        # carinfo = cardict[1]

        # carinfo = json.loads(str(cardict))
        car_info_objects = []
        for item in _newlist:
            if float(item['value']) > 0:
                car_info_objects.append(
                    CarInfo(
                        gs_id=gs,
                        tarikh=tarikh,
                        carstatus_id=item['key'],
                        amount=item['value']
                    )
                )

        if car_info_objects:
            # حذف رکوردهای قدیمی و ایجاد جدید به صورت bulk
            CarInfo.objects.filter(gs__gsid=gsid, tarikh=tarikh).delete()
            CarInfo.objects.bulk_create(car_info_objects)
    except:
        pass


def insert_waybill_gs(input_string, gs):
    input_string = input_string.strip()

    # حذف کاراکترهای اضافی در انتها
    input_string = re.sub(r'\]+\s*\d*$', '', input_string)
    input_string = re.sub(r',\s*$', '', input_string)

    # بررسی و اصلاح رشته JSON
    if input_string.startswith('[{"') and not input_string.endswith(']'):
        input_string = input_string + ']'
    elif input_string.startswith('{"') and not input_string.startswith('[{"'):
        input_string = '[' + input_string + ']'

    try:
        # تلاش برای تجزیه JSON
        waybills_data = json.loads(input_string)
        for item in waybills_data:
            try:
                _barname=Waybill.objects.get(waybill_id=item['in'],gsid_id=gs)
                _barname.send_type_id = 5
                _barname.save()
            except Waybill.DoesNotExist:
                pass
            WaybillGs.objects.update_or_create(
                waybill_number=item['in'],
                defaults={
                    'gs_id': gs,
                    'tarikh': item['op'][:10],
                    'waybill_amount': int(item['q'][:5])
                }
            )

    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass
