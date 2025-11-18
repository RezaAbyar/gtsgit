import base64
import datetime
import hashlib
import zlib
from django.contrib.auth.models import User
from django.db.models import Sum, Count, When, Case
import json

from accounts.models import Logs
from .models import IpcLog, IpcLogHistory, SellGs, CarInfo, Mojodi, ModemDisconnect
from base.models import Owner, GsModel, Pump, Ticket, Workflow, Parametrs, GsList, CloseGS
import jdatetime
from .models import SellModel
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .services.data_saver import DataSaver
from .services.qr_parser import QRParser

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


def load_code(qr, id):
    inputcode = qr.split(":")
    if inputcode[0] == inputcode[1]:

        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)
        return encrypt(id, 1, 1, 1, 1, 1, 1)
    else:
        print(2)
        Owner.commit_qrcode(qrcodes=str(inputcode[2]), id=id)
        print('please scan new code')


def encrypt(id, st, ticket, userid, lat, long, failure):
    owner = Owner.objects.get(id=id)
    qr_data = owner.qrcode

    try:
        # Parse QR data
        from .services.utils import process_qr_code
        _data = process_qr_code(qr_data, owner.id)

        parser = QRParser()
        parsed_data = parser.parse_qr_data(_data)

        # Save data to database
        saver = DataSaver(id, parsed_data)

        result = saver.save_all()
        if st == 2:  # RPM case
            from base.models import Ticket, Workflow
            ticket = Ticket.objects.get(id=ticket)
            ticket.closedate = datetime.now()
            ticket.status_id = 2
            ticket.save()

            Workflow.objects.create(
                ticket_id=ticket,
                user_id=userid,
                description='بستن تیکت RPM توسط تکنسین',
                organization_id=1,
                failure_id=failure,
                lat=lat,
                lang=long
            )
            return redirect('base:closeTicket')

        return result

    except Exception as e:
        Logs.objects.create(
            parametr1='مشکل رمزنگاری در رمزینه',
            parametr2=qr_data,
            owner_id=owner.id
        )
        return redirect('sell:listsell')


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
        yarane = 0
        azad = 0
        ezterari = 0
        haveleh = 0
        azmayesh = 0

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
            try:
                pump_number = int(sellitem[0])
                if pump_number <= 0:  # شماره پمپ نامعتبر
                    continue
            except (ValueError, IndexError):
                continue
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

            pomp = Pump.objects.get(number=pump_number , gs_id=gs)
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
