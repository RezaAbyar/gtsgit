from api.samplekey import decrypt as Decrypt
from lock.models import LockModel
from util import DENY_PERMISSSION, DENY_PAGE, HOME_PAGE
from django.shortcuts import render, redirect
from accounts.logger import add_to_log
from pay.models import StoreHistory
from .models import GsModel, UserPermission, DefaultPermission, Ticket, Pump, FailureCategory, Zone, Area, Owner
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q, Case, When, F
from operator import itemgetter
from django.db.models.functions import TruncDate
from .views import zoneorarea
from datetime import timedelta
from django.utils import timezone
from jalali_date import datetime2jalali

import jdatetime


def reportzoneticketmgr(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    add_to_log(request, f' مشاهده گزارش تیکت های جایگاه', 0)
    _list = None

    _sum = None
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)
    zones = Zone.objects_limit.all()

    if request.method == 'POST':
        datein = str(request.POST.get('select'))
        dateout = str(request.POST.get('select2'))
        if request.user.owner.role.role in 'mgr,setad':
            zoner = str(request.POST.get('select3'))
            if zoner:

                if zoner == "0":
                    _role = 'setad'
                    _roleid = 0
                else:
                    _role = 'zone'
                    _roleid = int(zoner)
        else:
            zoner = 0

        az = datein
        ta = dateout

        if len(datein) < 10:
            datein = "2020-10-10"
            dateout = "2100-12-20"
        else:
            datein = datein.split("/")
            dateout = dateout.split("/")
            datein = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            dateout = jdatetime.date(day=int(dateout[2]), month=int(dateout[1]), year=int(dateout[0])).togregorian()
        # datein = str(datein) + " 00:00:00"
        # dateout = str(dateout) + " 23:59:59"

        _list = Ticket.object_role.c_gs(request, 0).values('gs__area__zone__name', 'gs__area__zone_id',
                                                           ).filter(create__gte=datein,
                                                                    create__lte=dateout).annotate(
            count_all_ticket=Count('id'),
            count_change_all=Count(
                Case(When(serialmaster__gte=1, then=1))) + Count(
                Case(When(serialpinpad__gte=1, then=1))),
            count_change_master=Count(
                Case(When(serialmaster__gte=1, then=1))),
            count_change_pinpad=Count(
                Case(When(serialpinpad__gte=1, then=1))),
            count_open=Count(
                Case(When(status_id=1, then=1))),
            count_close=Count(
                Case(When(status_id=2, then=1))),
            count_feyk=Count(
                Case(When(reply_id__in=[50, 54], then=1))),
            count_test_close=Count(
                Case(When(status_id=2, actioner__role_id=7, then=1))),
            count_fani_close=Count(
                Case(When(status_id=2, actioner__role_id=8, then=1))),
            count_tek_close=Count(
                Case(When(status_id=2, actioner__role_id=2, then=1))),
            count_engin_close=Count(
                Case(When(status_id=2, actioner__role_id=103, then=1))),
            count_napaydari_day=Sum(
                Case(When(failure_id=1056, then='timeaction'))),
            star_avg=Avg(
                Case(When(star__lte=5, then='star'))),
            count_sla_avg=Sum('timeaction') / Count('id'),

        )

        _sum = Ticket.object_role.c_gs(request, 0).filter(create__gte=datein,
                                                          create__lte=dateout).aggregate(
            count_all_ticket=Count('id'),
            count_change_all=Count(
                Case(When(serialmaster__gte=1, then=1))) + Count(
                Case(When(serialpinpad__gte=1, then=1))),
            count_change_master=Count(
                Case(When(serialmaster__gte=1, then=1))),
            count_change_pinpad=Count(
                Case(When(serialpinpad__gte=1, then=1))),
            count_open=Count(
                Case(When(status_id=1, then=1))),
            count_close=Count(
                Case(When(status_id=2, then=1))),
            count_feyk=Count(
                Case(When(reply_id__in=[50, 54], then=1))),
            count_test_close=Count(
                Case(When(status_id=2, actioner__role_id=7, then=1))),
            count_fani_close=Count(
                Case(When(status_id=2, actioner__role_id=8, then=1))),
            count_tek_close=Count(
                Case(When(status_id=2, actioner__role_id=2, then=1))),
            count_engin_close=Count(
                Case(When(status_id=2, actioner__role_id=103, then=1))),
            count_napaydari_day=Sum(
                Case(When(failure_id=1056, then='timeaction'))),
            star_avg=Avg(
                Case(When(star__lte=5, then='star'))),
            count_sla_avg=Sum('timeaction') / Count('id'),
        )
    else:
        az = ""
        ta = ""
        datein = ""
        dateout = ""
        zoner = 0
    context = {'zones': zones, 'list': _list, 'az': az, 'ta': ta, 'sumkol': _sum, 'zoner': int(zoner), 'status': 1,
               'datein': datein, 'dateout': dateout, 'formpermmision': formpermmision}
    return render(request, 'report/reportgsticketmgr.html', context)


def reportareaticketmgr(request, _id, _az, _ta):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    if len(str(_id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    _id = Decrypt(_id)
    _list = None

    _sum = None
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)

    az = _az
    ta = _ta

    datein = az
    dateout = ta
    # datein = str(datein) + " 00:00:00"
    # dateout = str(dateout) + " 23:59:59"

    _list = Ticket.object_role.c_gs(request, 0).values('gs__area__zone__name', 'gs__area__zone_id',
                                                       'gs__area__name', 'gs__area_id',
                                                       ).filter(create__gte=datein, gs__area__zone_id=_id,
                                                                create__lte=dateout).annotate(
        count_all_ticket=Count('id'),
        count_change_all=Count(
            Case(When(serialmaster__gte=1, then=1))) + Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_change_master=Count(
            Case(When(serialmaster__gte=1, then=1))),
        count_change_pinpad=Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_open=Count(
            Case(When(status_id=1, then=1))),
        count_close=Count(
            Case(When(status_id=2, then=1))),
        count_feyk=Count(
            Case(When(reply_id__in=[50, 54], then=1))),
        count_test_close=Count(
            Case(When(status_id=2, actioner__role_id=7, then=1))),
        count_fani_close=Count(
            Case(When(status_id=2, actioner__role_id=8, then=1))),
        count_tek_close=Count(
            Case(When(status_id=2, actioner__role_id=2, then=1))),
        count_engin_close=Count(
            Case(When(status_id=2, actioner__role_id=103, then=1))),
        count_napaydari_day=Sum(
            Case(When(failure_id=1056, then='timeaction'))),
        star_avg=Avg(
            Case(When(star__lte=5, then='star'))),
        count_sla_avg=Sum('timeaction') / Count('id'),

    )

    _sum = Ticket.object_role.c_gs(request, 0).filter(create__gte=datein, gs__area__zone_id=_id,
                                                      create__lte=dateout).aggregate(
        count_all_ticket=Count('id'),
        count_change_all=Count(
            Case(When(serialmaster__gte=1, then=1))) + Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_change_master=Count(
            Case(When(serialmaster__gte=1, then=1))),
        count_change_pinpad=Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_open=Count(
            Case(When(status_id=1, then=1))),
        count_close=Count(
            Case(When(status_id=2, then=1))),
        count_feyk=Count(
            Case(When(reply_id__in=[50, 54], then=1))),
        count_test_close=Count(
            Case(When(status_id=2, actioner__role_id=7, then=1))),
        count_fani_close=Count(
            Case(When(status_id=2, actioner__role_id=8, then=1))),
        count_tek_close=Count(
            Case(When(status_id=2, actioner__role_id=2, then=1))),
        count_engin_close=Count(
            Case(When(status_id=2, actioner__role_id=103, then=1))),
        count_napaydari_day=Sum(
            Case(When(failure_id=1056, then='timeaction'))),
        star_avg=Avg(
            Case(When(star__lte=5, then='star'))),
        count_sla_avg=Sum('timeaction') / Count('id'),
    )

    context = {'list': _list, 'az': az, 'ta': ta, 'sumkol': _sum, 'status': 2, 'datein': datein, 'dateout': dateout,
               'formpermmision': formpermmision}
    return render(request, 'report/reportgsticketmgr.html', context)


def reportgsticketmgr(request, _id, _az, _ta):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    if len(str(_id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    _id = Decrypt(_id)
    _list = None

    _sum = None
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)

    az = _az
    ta = _ta

    datein = az
    dateout = ta
    # datein = str(datein) + " 00:00:00"
    # dateout = str(dateout) + " 23:59:59"

    _list = Ticket.object_role.c_gs(request, 0).values('gs_id', 'gs__area__zone__name', 'gs__area__zone_id',
                                                       'gs__area_id', 'gs__area__name',
                                                       'gs__name', 'gs__gsid').filter(create__gte=datein,
                                                                                      gs__area_id=_id,
                                                                                      create__lte=dateout).annotate(
        count_all_ticket=Count('id'),
        count_change_all=Count(
            Case(When(serialmaster__gte=1, then=1))) + Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_change_master=Count(
            Case(When(serialmaster__gte=1, then=1))),
        count_change_pinpad=Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_open=Count(
            Case(When(status_id=1, then=1))),
        count_close=Count(
            Case(When(status_id=2, then=1))),
        count_feyk=Count(
            Case(When(reply_id__in=[50, 54], then=1))),
        count_test_close=Count(
            Case(When(status_id=2, actioner__role_id=7, then=1))),
        count_fani_close=Count(
            Case(When(status_id=2, actioner__role_id=8, then=1))),
        count_tek_close=Count(
            Case(When(status_id=2, actioner__role_id=2, then=1))),
        count_engin_close=Count(
            Case(When(status_id=2, actioner__role_id=103, then=1))),
        count_napaydari_day=Sum(
            Case(When(failure_id=1056, then='timeaction'))),
        star_avg=Avg(
            Case(When(star__lte=5, then='star'))),
        count_sla_avg=Sum('timeaction') / Count('id'),

    )

    _sum = Ticket.object_role.c_gs(request, 0).filter(create__gte=datein, gs__area_id=_id,
                                                      create__lte=dateout).aggregate(
        count_all_ticket=Count('id'),
        count_change_all=Count(
            Case(When(serialmaster__gte=1, then=1))) + Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_change_master=Count(
            Case(When(serialmaster__gte=1, then=1))),
        count_change_pinpad=Count(
            Case(When(serialpinpad__gte=1, then=1))),
        count_open=Count(
            Case(When(status_id=1, then=1))),
        count_close=Count(
            Case(When(status_id=2, then=1))),
        count_feyk=Count(
            Case(When(reply_id__in=[50, 54], then=1))),
        count_test_close=Count(
            Case(When(status_id=2, actioner__role_id=7, then=1))),
        count_fani_close=Count(
            Case(When(status_id=2, actioner__role_id=8, then=1))),
        count_tek_close=Count(
            Case(When(status_id=2, actioner__role_id=2, then=1))),
        count_engin_close=Count(
            Case(When(status_id=2, actioner__role_id=103, then=1))),
        count_napaydari_day=Sum(
            Case(When(failure_id=1056, then='timeaction'))),
        star_avg=Avg(
            Case(When(star__lte=5, then='star'))),
        count_sla_avg=Sum('timeaction') / Count('id'),
    )

    context = {'list': _list, 'az': az, 'ta': ta, 'sumkol': _sum, 'status': 3, 'datein': datein, 'dateout': dateout,
               'formpermmision': formpermmision}
    return render(request, 'report/reportgsticketmgr.html', context)


def reportnesbatgs(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    add_to_log(request, f' مشاهده فرم نمودار نسبت خرابی', 0)
    areas = None
    zones = None
    a = 0
    if request.user.owner.role.role in ["setad", "mgr", "test", "fani"]:
        zones = Zone.objects.all()
    if request.user.owner.role.role == "zone":
        areas = Area.objects.filter(zone=request.user.owner.zone_id)

    if request.method == 'POST':

        store_type = request.POST.get('store_type', None)
        area_list = request.POST.get('area_list', None)
        area_list = area_list if area_list else 0

        amarticketgs = Ticket.objects.values('gs_id').all().annotate(
            mastergs=Count(Case(When(failure_id=1045, then=1))),
            pinpadgs=Count(Case(When(reply_id__in=[3, 4], then=1))))
        if area_list == '0':
            amarticketgs.filter(gs__area__zone_id=request.user.owner.zone_id)

        else:
            amarticketgs = amarticketgs.filter(gs__area_id=int(area_list))
        nazels = GsModel.objects.filter(area__zone_id=request.user.owner.zone_id).annotate(nazel=Count('gsall__id'))
        _list = []
        for item in amarticketgs:
            for nazel in nazels:
                if item['gs_id'] == nazel.id:
                    dict = {
                        'id': item['gs_id'],
                        'name': nazel.name + '( ' + nazel.area.name + ' )',
                        'master': round(int(item['mastergs']) / int(nazel.nazel), 1),
                        'pinpad': round(int(item['pinpadgs']) / int(nazel.nazel), 1),
                        'kol': round((int(item['mastergs']) + int(item['pinpadgs'])) / int(nazel.nazel), 1),
                    }
                    _list.append(dict)
                    break
        if area_list == '99990':
            _list = []
            amarticketgs = Ticket.objects.filter(gs__area__zone_id=request.user.owner.zone_id).values('gs__area_id',
                                                                                                      'gs__area__name').all().annotate(
                mastergs=Count(Case(When(failure_id=1045, then=1))),
                pinpadgs=Count(Case(When(reply_id__in=[3, 4], then=1))))
            nazels = Pump.objects.filter(gs__area__zone_id=request.user.owner.zone_id, status__status=True).count()

            for item in amarticketgs:
                dict = {
                    'id': item['gs__area_id'],
                    'name': item['gs__area__name'],
                    'master': round(int(item['mastergs']) / int(nazels), 1),
                    'pinpad': round(int(item['pinpadgs']) / int(nazels), 1),
                    'kol': round((int(item['mastergs']) + int(item['pinpadgs'])) / int(nazels), 1),
                }
                _list.append(dict)

        a = 0
        masterlist = sorted(_list, key=itemgetter('kol'), reverse=True)
        if store_type == 'master':
            a = 1
            masterlist = sorted(_list, key=itemgetter('master'), reverse=True)
        elif store_type == 'pinpad':
            a = 2
            masterlist = sorted(_list, key=itemgetter('pinpad'), reverse=True)
        elif store_type == 'all':
            a = 3
            masterlist = sorted(_list, key=itemgetter('kol'), reverse=True)

        context = {'masterlist': masterlist, 'areas': areas, 'zones': zones, 'a': int(a), 'store_type': store_type,
                   'area_list': int(area_list), 'formpermmision': formpermmision}
    else:
        context = {'areas': areas, 'zones': zones, 'a': 0, 'formpermmision': formpermmision}

    return render(request, 'report/report_nesbat.html', context)


def nesbat_tickets(request, id):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    _list = []
    add_to_log(request, f'گزارش مدیریتی تیکت ها ', 0)
    if request.user.owner.role.role in ['zone']:
        zone = Zone.objects_limit.filter(id=request.user.owner.zone_id).exclude(id=9).order_by('id')
    elif request.user.owner.role.role in ['setad', 'mgr', 'fani', 'test', 'posht']:
        zone = Zone.objects_limit.all().exclude(id=9).order_by('id')
    else:
        messages.warning(request, DENY_PERMISSSION)
        return redirect(HOME_PAGE)
    s_master = 0

    s_pinpad = 0

    summ = 0
    sum_gs = 0
    sum_pump = 0
    sum_ticket = 0
    sum_master = 0
    sum_pinpad = 0
    count_gs_all = GsModel.objects.filter(status_id=1).count()
    count_pump_all = Pump.objects.filter(status__status=True,
                                         gs__status_id=1).count()
    count_ticket_all = Ticket.objects.exclude(organization_id=4).filter(status_id=1,
                                                                        gs__status__status=True,
                                                                        Pump__status__status=True,
                                                                        failure__failurecategory_id__in=[1010,
                                                                                                         1011]).count()

    store_all = StoreHistory.objects.filter(status_id=3).count()
    for gs in zone:
        count_gs_zone = GsModel.objects.filter(area__zone_id=gs.id, status_id=1).count()

        count_pump_zone = Pump.objects.filter(gs__area__zone_id=gs.id, status__status=True,
                                              gs__status_id=1).count()

        count_ticket_zone = Ticket.objects.exclude(organization_id=4).filter(gs__area__zone_id=gs.id, status_id=1,
                                                                             gs__status__status=True,
                                                                             Pump__status__status=True,
                                                                             failure__failurecategory_id__in=[1010,
                                                                                                              1011]).count()
        store_zone = StoreHistory.objects.filter(status_id=3, owner__zone_id=gs.id).count()

        gs_nesbat = (count_gs_zone / count_gs_all) * 100
        pomp_nesbat = (count_pump_zone / count_pump_all) * 100
        ticket_nesbat = (count_ticket_zone / count_ticket_all) * 100
        store_nesbat = (store_zone / store_all) * 100
        storenazel_nesbat = (store_nesbat - pomp_nesbat)

        _dict = {
            'st': 0,
            'id': gs.id,
            'name': gs.name,
            'count_gs': count_gs_zone,
            'count_pump': count_pump_zone,
            'count_ticket': count_ticket_zone,
            'gs_nesbat': round(gs_nesbat, 2),
            'pomp_nesbat': round(pomp_nesbat, 2),
            'ticket_nesbat': round(ticket_nesbat, 2),
            'store_nesbat': round(store_nesbat, 2),
            'store_zone': store_zone,
            'storenazel_nesbat': round(storenazel_nesbat, 2),

        }
        _list.append(_dict)
        _list = sorted(_list, key=itemgetter('gs_nesbat'), reverse=True)
        # sum_gs += count_gs
        # sum_pump += count_pump
        # sum_ticket += count_ticket

    if id == 1:
        _list = sorted(_list, key=itemgetter('gs_nesbat'), reverse=True)
    elif id == 2:
        _list = sorted(_list, key=itemgetter('pomp_nesbat'), reverse=True)
    elif id == 3:
        _list = sorted(_list, key=itemgetter('ticket_nesbat'), reverse=True)
    elif id == 4:
        _list = sorted(_list, key=itemgetter('store_nesbat'), reverse=True)
    elif id == 5:
        _list = sorted(_list, key=itemgetter('storenazel_nesbat'), reverse=True)
    elif id == 6:
        _list = sorted(_list, key=itemgetter('store_zone'), reverse=True)

    context = {'list': _list, 'id': id, 'formpermmision': formpermmision}
    return render(request, 'report/nesbat_tickets.html', context)


def reporttecnesianmgr(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    add_to_log(request, f' مشاهده فرم پلمپ و تیکت تکنسین', 0)
    report_data = None
    count_closed_tickets = 0
    open_tickets = 0
    day = 0
    _sum = None
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)
    az = ""
    ta = ""
    zoner = 0
    if request.user.owner.role.role == 'zone':
        zones = Owner.objects.filter(role__role='tek', zone_id=request.user.owner.zone.id)
    else:
        zones = Owner.objects.filter(role__role='tek')

    if request.method == 'POST':
        datein = str(request.POST.get('select'))
        dateout = str(request.POST.get('select2'))
        zoner = str(request.POST.get('select3'))

        az = datein
        ta = dateout

        if len(datein) < 10:
            datein = "2020-10-10"
            dateout = "2100-12-20"
        else:
            datein = datein.split("/")
            dateout = dateout.split("/")
            datein = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
            dateout = jdatetime.date(day=int(dateout[2]), month=int(dateout[1]), year=int(dateout[0])).togregorian()

        start_date = datein
        end_date = dateout

        date_range = end_date - start_date
        date_list = [start_date + timedelta(days=x) for x in range(date_range.days + 1)]
        # فیلتر پایه برای تکنسین‌ها
        tech = Owner.objects.get(id=zoner)
        report_data = []
        for day in date_list:
            next_day = day + timedelta(days=1)
            closed_tickets = Ticket.objects.exclude(organization_id=4).filter(
                failure__failurecategory_id__in=[1010, 1011],
                actioner=tech,
                closedate__date=day,
                status_id=2  # تیکت‌های بسته شده
            )
            count_closed_tickets = closed_tickets.count()
            i = 0
            for ticket in closed_tickets:
                if LockModel.objects.filter(ticket=ticket).count() > 0:
                    i += 1

            open_tickets = Ticket.objects.exclude(organization_id=4).filter(
                gs__gsowner__owner_id=tech,
                create__date__lte=day,
                closedate__date__gte=day, failure__failurecategory_id__in=[1010, 1011],

            ).count()

            report_data.append({
                'day': day,
                'nolock': i,
                'closed_tickets': count_closed_tickets,
                'open_tickets': open_tickets,
                'technician_name': tech.get_full_name(),
                'zone_name': tech.zone.name if tech.zone else '',
            })

    context = {'list': report_data, 'zones': zones, 'zoner': int(zoner), 'az': az, 'ta': ta,
               'formpermmision': formpermmision}
    return render(request, 'report/reporttecnesianmgr.html', context)


def ticket_trend_report(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    # دریافت پارامترهای فیلتر
    report_type = request.GET.get('report_type', '15days')  # 15days, monthly
    year = int(request.GET.get('year', datetime2jalali(timezone.now()).year))
    month = int(request.GET.get('month', datetime2jalali(timezone.now()).month))
    zone_id = request.GET.get('zone_id')
    failure_category = request.GET.get('failure_category')

    # محاسبه محدوده تاریخ شمسی
    jalali_start = jdatetime.date(year, month, 1)
    jalali_end = jdatetime.date(year, month, 31)

    # تبدیل به تاریخ میلادی برای کوئری

    start_date = jdatetime.date(day=1, month=int(month), year=int(year)).togregorian()

    end_date = jdatetime.date(day=31, month=int(month), year=int(year)).togregorian()

    # ایجاد بازه‌های زمانی
    if report_type == '15days':
        # تقسیم ماه به دو بازه 15 روزه
        periods = [
            {
                'name': '1 تا 15 ماه',
                'jalali_start': jdatetime.date(year, month, 1),
                'jalali_end': jdatetime.date(year, month, 15),
                'start': start_date,
                'end': start_date + timedelta(days=14)
            },
            {
                'name': '16 تا پایان ماه',
                'jalali_start': jdatetime.date(year, month, 16),
                'jalali_end': jalali_end,
                'start': start_date + timedelta(days=15),
                'end': end_date
            }
        ]
    else:
        # کل ماه به عنوان یک بازه
        periods = [
            {
                'name': 'کل ماه',
                'jalali_start': jalali_start,
                'jalali_end': jalali_end,
                'start': start_date,
                'end': end_date
            }
        ]

    # دریافت لیست مناطق برای فیلتر
    if request.user.owner.role.role in ['mgr', 'setad']:
        zones = Zone.objects_limit.all()
    elif request.user.owner.role.role in ['zone']:
        zones = Zone.objects.filter(id=request.user.owner.zone_id)

    # جمع‌آوری داده‌ها برای هر منطقه
    report_data = []
    for zone in zones:
        if zone_id and str(zone.id) != zone_id:
            continue

        zone_data = {
            'zone_name': zone.name,
            'periods': []
        }

        for period in periods:
            # فیلتر پایه برای تیکت‌ها
            tickets = Ticket.objects.filter(
                create__date__gte=period['start'],
                create__date__lte=period['end'],
                gs__area__zone=zone
            )

            # اعمال فیلترهای اضافی
            if failure_category:
                tickets = tickets.filter(failure__failurecategory_id=failure_category)

            # محاسبه آمارها
            total_tickets = tickets.count()
            closed_tickets = tickets.filter(status_id=2).count()
            open_tickets = tickets.filter(status_id=1).count()

            # میانگین زمان رسیدگی
            resolution = tickets.filter(status_id=2).aggregate(
                avg_time=Avg(F('closedate') - F('create'))
            )
            avg_hours = resolution['avg_time'].total_seconds() / 3600 if resolution['avg_time'] else 0

            # 5 خرابی پرتکرار
            top_failures = tickets.values(
                'failure__info',
                'failure__failurecategory__info'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            zone_data['periods'].append({
                'period_name': period['name'],
                'jalali_range': f"{period['jalali_start'].strftime('%Y/%m/%d')} تا {period['jalali_end'].strftime('%Y/%m/%d')}",
                'total_tickets': total_tickets,
                'closed_tickets': closed_tickets,
                'open_tickets': open_tickets,
                'avg_resolution_hours': round(avg_hours, 1),
                'top_failures': list(top_failures)
            })

        report_data.append(zone_data)

    # آماده کردن داده‌ها برای نمودار
    chart_data = {
        'zones': [item['zone_name'] for item in report_data],
        'periods': [period['name'] for period in periods],
        'datasets': []
    }

    # لیست دسته‌بندی خرابی‌ها برای فیلتر
    failure_categories = FailureCategory.objects.annotate(
        ticket_count=Count('failuresub__ticket')
    ).filter(ticket_count__gt=0)

    # سال‌ها و ماه‌های موجود برای انتخاب
    years = range(datetime2jalali(timezone.now()).year - 5, datetime2jalali(timezone.now()).year + 1)
    months = [
        (1, 'فروردین'), (2, 'اردیبهشت'), (3, 'خرداد'),
        (4, 'تیر'), (5, 'مرداد'), (6, 'شهریور'),
        (7, 'مهر'), (8, 'آبان'), (9, 'آذر'),
        (10, 'دی'), (11, 'بهمن'), (12, 'اسفند')
    ]
    comparison_data = {
        'labels': [period['name'] for period in periods],
        'datasets': []
    }

    colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e',
        '#e74a3b', '#858796', '#5a5c69', '#3a3b45'
    ]

    for i, zone in enumerate(zones):
        if zone_id and str(zone.id) != zone_id:
            continue

        zone_tickets = []
        for period in periods:
            tickets = Ticket.objects.filter(
                create__date__gte=period['start'],
                create__date__lte=period['end'],
                gs__area__zone=zone
            )
            if failure_category:
                tickets = tickets.filter(failure__failurecategory_id=failure_category)
            zone_tickets.append(tickets.count())

        comparison_data['datasets'].append({
            'label': zone.name,
            'data': zone_tickets,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)],
            'borderWidth': 1
        })

    trend_data = {
        'labels': [zone.name for zone in zones if not zone_id or str(zone.id) == zone_id],
        'datasets': [
            {
                'label': '15 روز اول',
                'data': [],
                'borderColor': '#4e73df',
                'backgroundColor': 'rgba(78, 115, 223, 0.05)',
                'borderWidth': 2,
                'tension': 0.1
            },
            {
                'label': '15 روز دوم',
                'data': [],
                'borderColor': '#1cc88a',
                'backgroundColor': 'rgba(28, 200, 138, 0.05)',
                'borderWidth': 2,
                'tension': 0.1
            }
        ]
    }

    for zone in zones:
        if zone_id and str(zone.id) != zone_id:
            continue

        # محاسبه برای 15 روز اول
        period1_start = start_date
        period1_end = start_date + timedelta(days=14)
        tickets1 = Ticket.objects.filter(
            create__date__gte=period1_start,
            create__date__lte=period1_end,
            gs__area__zone=zone
        )
        if failure_category:
            tickets1 = tickets1.filter(failure__failurecategory_id=failure_category)
        trend_data['datasets'][0]['data'].append(tickets1.count())

        # محاسبه برای 15 روز دوم
        period2_start = start_date + timedelta(days=15)
        tickets2 = Ticket.objects.filter(
            create__date__gte=period2_start,
            create__date__lte=end_date,
            gs__area__zone=zone
        )
        if failure_category:
            tickets2 = tickets2.filter(failure__failurecategory_id=failure_category)
        trend_data['datasets'][1]['data'].append(tickets2.count())

    context = {
        'formpermmision': formpermmision,
        'trend_data': trend_data,
        'comparison_data': comparison_data,
        'report_data': report_data,
        'chart_data': chart_data,
        'report_type': report_type,
        'years': years,
        'months': months,
        'selected_year': year,
        'selected_month': month,
        'zones': zones,
        'failure_categories': failure_categories,
        'selected_zone': int(zone_id) if zone_id else None,
        'selected_category': int(failure_category) if failure_category else None
    }
    add_to_log(request, f' مشاهده گزارش ترند خرابی', 0)
    return render(request, 'trend_report.html', context)


def pump_ticket_percentage_report(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    report_type = 'master'
    # دریافت پارامترهای فیلتر
    if request.method == 'POST':
        add_to_log(request, f' مشاهده گزارش درصد تیکت ها', 0)
        selected_zone = request.POST.get('zone', 0)
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        report_type = request.POST.get('report_type', 'all')

        if report_type == 'all':
            _failure = [1010, 1011]
        elif report_type == 'master':
            _failure = [1010]
        elif report_type == 'pinpad':
            _failure = [1011]

        # تنظیم تاریخ‌های پیش‌فرض اگر ارسال نشده باشند
        if not from_date or not to_date:
            to_date = jdatetime.date.today().strftime('%Y/%m/%d')
            from_date = (jdatetime.date.today() - jdatetime.timedelta(days=365)).strftime('%Y/%m/%d')

        # تبدیل تاریخ‌های جلالی به میلادی
        try:
            from_date_jalali = jdatetime.date(*map(int, from_date.split('/')))
            to_date_jalali = jdatetime.date(*map(int, to_date.split('/')))

            from_date_gregorian = from_date_jalali.togregorian()
            to_date_gregorian = to_date_jalali.togregorian()
        except:
            messages.error(request, 'فرمت تاریخ وارد شده صحیح نیست')
            return redirect(request.path)

        # محاسبه ماه‌های موجود در بازه شمسی
        months_jalali = []
        current_date_jalali = from_date_jalali.replace(day=1)

        while current_date_jalali <= to_date_jalali:
            months_jalali.append(current_date_jalali.strftime('%Y/%m'))
            # حرکت به ماه بعد
            if current_date_jalali.month == 12:
                current_date_jalali = current_date_jalali.replace(year=current_date_jalali.year + 1, month=1)
            else:
                current_date_jalali = current_date_jalali.replace(month=current_date_jalali.month + 1)

        # دریافت تمام مناطق
        if request.user.owner.role.role in ['mgr', 'setad']:
            zones = Zone.objects_limit.all()
        elif request.user.owner.role.role in ['zone']:
            zones = Zone.objects.filter(id=request.user.owner.zone_id)

        # آماده‌سازی داده‌های گزارش
        report_data = []

        # فیلتر بر اساس منطقه اگر انتخاب شده باشد
        zone_filter = Q()
        if selected_zone and selected_zone != '0':
            zone_filter = Q(area__zone_id=selected_zone)

        # برای هر منطقه محاسبات را انجام می‌دهیم
        for zone in zones.filter(zone_filter) if selected_zone != '0' else zones:
            zone_data = {
                'zone_id': zone.id,
                'zone_name': zone.name,
                'total_pumps': 0,
                'months': []
            }

            # محاسبه برای هر ماه شمسی
            current_month_jalali = from_date_jalali.replace(day=1)
            while current_month_jalali <= to_date_jalali:
                # محاسبه شروع و پایان ماه شمسی
                month_start_jalali = current_month_jalali.replace(day=1)
                if current_month_jalali.month == 12:
                    month_end_jalali = jdatetime.date(current_month_jalali.year, 12, 29)
                    # بررسی اینکه آیا روز 30 اسفند وجود دارد یا خیر
                    try:
                        month_end_jalali = jdatetime.date(current_month_jalali.year, 12, 30)
                    except:
                        pass
                else:
                    month_end_jalali = jdatetime.date(
                        current_month_jalali.year,
                        current_month_jalali.month + 1,
                        1
                    ) - jdatetime.timedelta(days=1)

                # تبدیل به میلادی برای کوئری
                month_start_gregorian = month_start_jalali.togregorian()
                month_end_gregorian = month_end_jalali.togregorian()

                # تعداد کل تیکت‌ها در این ماه و منطقه
                total_tickets = Ticket.objects.filter(
                    gs__area__zone=zone,
                    create__date__range=[month_start_gregorian, month_end_gregorian]
                ).count()

                # تعداد تیکت‌های مربوط به خرابی‌های مورد نظر
                tickets_with_failure = Ticket.objects.filter(
                    gs__area__zone=zone,
                    create__date__range=[month_start_gregorian, month_end_gregorian],
                    failure__failurecategory__in=_failure
                ).count()

                # محاسبه درصد
                percentage = 0
                if total_tickets > 0:
                    percentage = round((tickets_with_failure / total_tickets) * 100, 2)

                zone_data['months'].append({
                    'month': current_month_jalali.strftime('%Y/%m'),
                    'percentage': round(percentage),
                    'total_tickets': total_tickets,
                    'tickets_with_failure': tickets_with_failure
                })

                # حرکت به ماه بعد شمسی
                if current_month_jalali.month == 12:
                    current_month_jalali = current_month_jalali.replace(year=current_month_jalali.year + 1, month=1)
                else:
                    current_month_jalali = current_month_jalali.replace(month=current_month_jalali.month + 1)

            # محاسبه کل تیکت‌های منطقه در کل بازه زمانی
            zone_data['total_pumps'] = sum(month['total_tickets'] for month in zone_data['months'])

            report_data.append(zone_data)

        context = {
            'formpermmision': formpermmision,
            'zones': zones,
            'selected_zone': selected_zone,
            'from_date': from_date,
            'to_date': to_date,
            'months': months_jalali,
            'report_data': report_data,
            'report_type': report_type,
        }
    else:
        context = {
            'formpermmision': formpermmision,
            'report_type': report_type,
            'from_date': jdatetime.date.today().strftime('%Y/%m/%d'),
            'to_date': jdatetime.date.today().strftime('%Y/%m/%d'),
        }

    return render(request, 'report/pump_ticket_percentage.html', context)


def generate_failure_report(zone_id=None, start_date=None, end_date=None, report_type='daily'):
    _day = 1
    # فیلترهای پایه
    tickets = Ticket.objects.all()
    pumps = Pump.objects.filter(status__status=True)  # فقط نازل‌های فعال

    # فیلتر بر اساس منطقه اگر مشخص شده باشد
    if zone_id:
        tickets = tickets.filter(gs__area__zone_id=zone_id)
        pumps = pumps.filter(gs__area__zone_id=zone_id)
    total_pumps_in_zone = pumps.count()  # تعداد کل نازل‌های منطقه

    # تبدیل تاریخ شمسی به میلادی اگر وارد شده باشد
    if start_date and end_date:
        start_date = jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian()
        end_date = jdatetime.datetime.strptime(end_date, '%Y/%m/%d').togregorian()
        tickets = tickets.filter(create__date__range=[start_date, end_date])
        _day = (end_date - start_date).days

    if report_type == 'daily':
        # گزارش روزانه
        data = tickets.annotate(
            date=TruncDate('create')
        ).values('date').annotate(
            total=Count('id'),
            cardreader=Count('id', filter=Q(failure__failurecategory_id=1010)),
            pinpad=Count('id', filter=Q(failure__failurecategory_id=1011))
        ).order_by('date')

        # محاسبه درصد بر اساس تعداد نازل‌ها
        if zone_id and total_pumps_in_zone > 0:
            for item in data:
                item['cardreader_percentage'] = round((item['cardreader'] / total_pumps_in_zone) * 100, 2)
                item['pinpad_percentage'] = round((item['pinpad'] / total_pumps_in_zone) * 100, 2)
        else:
            for item in data:
                item['cardreader_percentage'] = 0
                item['pinpad_percentage'] = 0

        # تبدیل تاریخ به شمسی برای نمایش
        dates = [datetime2jalali(item['date']).strftime('%Y/%m/%d') for item in data]
        cardreader_percentages = [item['cardreader_percentage'] for item in data]
        pinpad_percentages = [item['pinpad_percentage'] for item in data]

        chart_data = {
            'categories': dates,
            'series': [
                {
                    'name': 'درصد خرابی کارتخوان',
                    'data': cardreader_percentages
                },
                {
                    'name': 'درصد خرابی بین پد',
                    'data': pinpad_percentages
                }
            ]
        }

    elif report_type == 'monthly':
        # گزارش ماهانه
        data = tickets.annotate(
            month=F('create_shamsi_month'),
            year=F('create_shamsi_year')
        ).values('year', 'month').annotate(
            total=Count('id'),
            cardreader=Count('id', filter=Q(failure__failurecategory_id=1010)),
            pinpad=Count('id', filter=Q(failure__failurecategory_id=1011))
        ).order_by('year', 'month')

        # محاسبه درصد بر اساس تعداد نازل‌ها
        if zone_id and total_pumps_in_zone > 0:
            for item in data:
                item['cardreader_percentage'] = round(((item['cardreader'] / 30) / total_pumps_in_zone) * 100, 2)
                item['pinpad_percentage'] = round(((item['pinpad'] / 30) / total_pumps_in_zone) * 100, 2)
        else:
            for item in data:
                item['cardreader_percentage'] = 0
                item['pinpad_percentage'] = 0

        # نام ماه‌های شمسی
        month_names = {
            '1': 'فروردین', '01': 'فروردین',
            '2': 'اردیبهشت', '02': 'اردیبهشت',
            '3': 'خرداد', '03': 'خرداد',
            '4': 'تیر', '04': 'تیر',
            '5': 'مرداد', '05': 'مرداد',
            '6': 'شهریور', '06': 'شهریور',
            '7': 'مهر', '07': 'مهر',
            '8': 'آبان', '08': 'آبان',
            '9': 'آذر', '09': 'آذر',
            '10': 'دی',
            '11': 'بهمن',
            '12': 'اسفند',
            '': 'نامشخص'  # مقدار پیش‌فرض برای ماه‌های خالی
        }

        dates = []
        for item in data:
            month = str(item['month']) if item['month'] else ''
            year = str(item['year']) if item['year'] else 'نامشخص'
            month_name = month_names.get(month, 'نامشخص')
            dates.append(f"{month_name} {year}")

        dates = [f"{month_names[item['month']]} {item['year']}" for item in data]
        cardreader_percentages = [item['cardreader_percentage'] for item in data]
        pinpad_percentages = [item['pinpad_percentage'] for item in data]

        chart_data = {
            'categories': dates,
            'series': [
                {
                    'name': 'درصد خرابی کارتخوان',
                    'data': cardreader_percentages
                },
                {
                    'name': 'درصد خرابی بین پد',
                    'data': pinpad_percentages
                }
            ]
        }

    elif report_type == 'national':
        # گزارش کشوری
        zones = Zone.objects.all()
        dates = []
        cardreader_percentages = []
        pinpad_percentages = []

        for zone in zones:
            # تعداد نازل‌های هر منطقه
            total_pumps_in_zone = Pump.objects.filter(
                status__status=True
            ).count()

            # تعداد تیکت‌های هر منطقه
            zone_tickets = tickets.filter(gs__area__zone=zone)
            cardreader_count = zone_tickets.filter(failure__failurecategory_id=1010).count()
            pinpad_count = zone_tickets.filter(failure__failurecategory_id=1011).count()
            cardreader_count = cardreader_count / _day
            pinpad_count = pinpad_count / _day
            # محاسبه درصد
            cardreader_percentage = round((cardreader_count / total_pumps_in_zone) * 100,
                                          2) if total_pumps_in_zone > 0 else 0
            pinpad_percentage = round((pinpad_count / total_pumps_in_zone) * 100, 2) if total_pumps_in_zone > 0 else 0

            dates.append(zone.name)
            cardreader_percentages.append(cardreader_percentage)
            pinpad_percentages.append(pinpad_percentage)

        chart_data = {
            'categories': dates,
            'series': [
                {
                    'name': 'درصد خرابی کارتخوان',
                    'data': cardreader_percentages
                },
                {
                    'name': 'درصد خرابی بین پد',
                    'data': pinpad_percentages
                }
            ]
        }

    return {
        'chart_data': chart_data,
        'report_type': report_type
    }


def generate_failure_curve(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='report')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    """
    تابع اصلی برای ایجاد گزارش
    """
    chart_data = {
        'categories': '0',
        'series': [
            {
                'name': 'خرابی کارتخوان',
                'data': 0
            },
            {
                'name': 'خرابی بین پد',
                'data': 0
            }
        ]
    }
    if request.user.owner.role.role in ['setad', 'mgr', 'fani']:
        zones = Zone.objects_limit.all()
        zone_id = request.GET.get('zone_id')
    else:
        zones = Zone.objects.filter(id=request.user.owner.zone_id)
        zone_id = request.user.owner.zone_id

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'daily')
    if start_date and end_date:
        result = generate_failure_report(
            zone_id=zone_id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type
        )

        return render(request, 'report/chart_failure_report.html', {
            'zones': zones,
            'chart_data': result['chart_data'],
            'report_type': report_type,
            'formpermmision': formpermmision
        })
    return render(request, 'report/chart_failure_report.html', {
        'zones': zones,
        'chart_data': chart_data,
        'formpermmision': formpermmision
    })
