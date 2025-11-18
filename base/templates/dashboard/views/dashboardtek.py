from django.db.models import Count, Sum, Q, Avg, Case, When
from operator import itemgetter
from base.models import Workflow, Ticket, GsList, Pump, GsModel, Area, Owner
from cart.models import PanModels
from lock.models import LockModel
from pay.models import StoreList, Store
from sell.models import SellModel
from datetime import datetime, date
import jdatetime
from django.conf import settings
import datetime

unname = 'نا مشخص'


def dashboardtek(_refrenceid, _roleid, request):
    listmeticket = None
    benzin_kol = 0
    super_kol = 0
    gaz_kol = 0
    benzin_dis = 0
    super_dis = 0
    gaz_dis = 0
    sellamarlist = []
    arbain = []
    plomb = []
    list_gs = []
    listzone = []
    listnemodararea = []
    card_expire_count = 0
    card_expire_area_count = 0
    _today = date.today()
    listarea = []
    openticket = 0
    user_id = Owner.objects.get(id=_roleid).user_id
    mastersmojodi = StoreList.objects.filter(status_id__in=[4], statusstore_id=1,
                                             getuser_id=_roleid).count()
    pinpadsmojodi = StoreList.objects.filter(status_id__in=[4], statusstore_id=2,
                                             getuser_id=_roleid).count()
    mastersdaghi = StoreList.objects.filter(status_id__in=[6], statusstore_id=1,
                                            getuser_id=_roleid).count()
    pinpadsdaghi = StoreList.objects.filter(status_id__in=[6], statusstore_id=2,
                                            getuser_id=_roleid).count()
    daghi = StoreList.objects.filter(getuser_id=_roleid, status_id=6)
    plomb = LockModel.objects.filter(idg_user_id=user_id, status_id=6).order_by('-id')

    openticket = Ticket.object_role.c_gs(request, 0).filter(
        status__status='open').exclude(organization_id=4).count()


    closeticket = Ticket.object_role.c_gs(request, 0).annotate(count=Count('id')).filter(
        closedate__year=_today.year,
        closedate__month=_today.month,
        closedate__day=_today.day,
        status__status='close')
    closeticket = closeticket.count()

    listcloseticket = Ticket.object_role.c_gs(request, 0).values('close_shamsi_date').annotate(
        count=Count('id')).filter(status_id=2).order_by(
        '-close_shamsi_date')[:5]

    listcloseticket = sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)

    listopenticket = Ticket.object_role.c_gs(request, 0).values('shamsi_date').annotate(
        count=Count('id')).filter(
    ).exclude(organization_id=4).order_by('-shamsi_date')[:5]
    try:
        listopenticket = sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)
    except:
        print('1')
    listmeticket = Workflow.object_role.c_work_me(request).values('createdate').annotate(
        count=Count('id')).order_by('-createdate')[:5]
    listmeticket = sorted(listmeticket, key=itemgetter('createdate'), reverse=False)

    tekowner = Owner.objects.get(id=_roleid).zone_id
    store_noget = Store.object_role.c_base(request).filter(status_id=2,
                                                           ).aggregate(master=Sum('master'),
                                                                       pinpad=Sum('pinpad'))
    master_daghi = StoreList.object_role.c_base(request).filter(statusstore=1,
                                                                status_id__in=[6, 10, 11]).count()
    pinpad_daghi = StoreList.object_role.c_base(request).filter(statusstore=2,
                                                                status_id__in=[6, 10, 11]).count()
    masters = StoreList.object_role.c_base(request).filter(status_id__in=[3, 4], statusstore_id=1
                                                           ).count()
    store_takhsis = Store.object_role.c_base(request).filter(status_id=1,
                                                             ).aggregate(master=Sum('master'),
                                                                         pinpad=Sum('pinpad'))
    pinpads = StoreList.object_role.c_base(request).filter(status_id__in=[3, 4], statusstore_id=2
                                                           ).count()

    store_create_master = StoreList.object_role.c_base(request).filter(status_id=9,
                                                                       statusstore_id=1,
                                                                       ).count
    store_create_pinpad = StoreList.object_role.c_base(request).filter(status_id=9,
                                                                       statusstore_id=2,
                                                                       ).count

    count_master = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1010,
                                                              failure__isnazel=True).count()
    count_pinpad = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1011,
                                                              failure__isnazel=True).count()
    count_fani = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                            organization_id=2,
                                                            ).count()
    count_test = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                            organization_id=3,
                                                            ).count()
    count_engin = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                             organization_id=4,
                                                             ).count()
    count_area = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                            organization_id=7,
                                                            ).count()
    count_gs = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                          organization_id=8,
                                                          ).count()
    count_tek = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                           organization_id=1,
                                                           ).count()
    napaydari = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1056, status_id=1, is_system=True).count()
    rpm = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1164, status_id=1, is_system=True).count()
    napaydari_list = Ticket.object_role.c_gs(request, 0).filter(
        status__status='open', gs__active=True,
        failure_id=1056, status_id=1, is_system=True)
    openticketyesterday = Ticket.object_role.c_gs(request, 0).exclude(organization_id=4).filter(

        status__status='open', create__date__year=_today.year,
        create__date__month=_today.month,
        create__date__day=_today.day).count()

    napydarilist = []
    liststart = Ticket.object_role.c_gs(request, 0).filter(status__status='close',
                                                           star__gte=1, star__lte=5,
                                                           ).aggregate(
        star=Avg('star'), vote=Count('id'))
    if liststart['star']:
        stars = round(liststart['star'], 1)
    else:
        stars = 'امتیازی ثبت نشده'
    for item in napaydari_list:

        tekname = GsList.objects.filter(owner__role__role='tek', gs_id=item.gs_id, owner__active=True).first()
        if tekname:
            teknameowner = tekname.owner
        else:
            teknameowner = unname
        today = datetime.datetime.today()
        t1 = date(year=today.year, month=today.month, day=today.day)
        outdate = item.create
        t2 = date(year=outdate.year, month=outdate.month, day=outdate.day)
        tedad = (t1 - t2).days
        _dict = {
            'id': item.id,
            'gsid': item.gs.gsid,
            'name': item.gs.name,
            'nahye': item.gs.area.name,
            'tedad': tedad,
            'tek': teknameowner
        }
        napydarilist.append(_dict)
        napydarilist = sorted(napydarilist, key=itemgetter('tedad'), reverse=True)
    _today = date.today()
    napaydari_today = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        gs__active=True, create__date__year=_today.year, create__date__month=_today.month,
        create__date__day=_today.day,
        failure_id=1056, status_id=1, is_system=True).count()

    count_me = Ticket.object_role.c_me(request).exclude(organization_id=4).filter(
        status__status='open').count()

    _today = date.today()
    gscount = GsModel.object_role.c_gsmodel(request).filter(active=True).count()
    nazelcount = Pump.object_role.c_gs(request, 0).filter(gs__active=True,
                                                          active=True).count()
    this_date = datetime.datetime.today()
    gsmodel = GsModel.object_role.c_gsmodel(request).filter(active=True)
    nosell = gsmodel.exclude(
        id__in=SellModel.objects.filter(sell__gte=5, sellkol__gte=5,
                                        tarikh=this_date - datetime.timedelta(days=1)).values('gs_id')).count()
    date_nosell1 = jdatetime.date.today() - datetime.timedelta(days=1)
    date_nosell = str(date_nosell1)[5:]
    date_nosell = date_nosell.replace("-", "/")

    listgs = []
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

    return ({'openticket': openticket, 'closeticket': closeticket,
             'openticketyesterday': openticketyesterday, 'listmeTicket': listmeticket,
             'listCloseTicket': listcloseticket, 'listgs': listgs, 'plomb': plomb,
             'pinpadsdaghi': pinpadsdaghi, 'mastersdaghi': mastersdaghi,
             'listOpenTicket': listopenticket, 'napaydari_today': napaydari_today,
             'listarea': listarea, 'pinpadsmojodi': pinpadsmojodi, 'mastersmojodi': mastersmojodi,
             'count_master': count_master, 'napaydari': napaydari,
             'count_me': count_me, 'card_expire_area_count': card_expire_area_count,
             'count_pinpad': count_pinpad, 'count_fani': count_fani, 'count_engin': count_engin,
             'count_area': count_area, 'count_gs': count_gs,
             'sellamarlist': sellamarlist, 'daghi': daghi, 'date_nosell': date_nosell, 'nosell': nosell,
             'cards_expire': card_expire_count,
             'nazelcount': nazelcount, 'gscount': gscount, 'benzin_kol': benzin_kol,
             'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis,
             'listzone': listzone, 'list_gs': list_gs, 'listnemodararea': listnemodararea,
             'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm,
             'count_test': count_test, 'count_tek': count_tek, 'stars': stars, 'store_noget': store_noget,
             'master_daghi': master_daghi, 'pinpad_daghi': pinpad_daghi,
             'store_takhsis': store_takhsis, 'store_create_master': store_create_master, 'masters': masters,
             'pinpads': pinpads,
             'store_create_pinpad': store_create_pinpad,
             'napaydari_list': napydarilist})
