from django.db.models import Count, Sum, Q, Avg, OuterRef, Exists
from operator import itemgetter
from django.utils import timezone
from accounts.logger import add_to_log
from base.models import Workflow, Ticket, GsList, Pump, GsModel, TicketScience, Zone, StatusMoavagh
from cart.models import PanModels
from pay.models import StoreList, Store
from sell.models import SellModel
from datetime import datetime, date
import jdatetime
import datetime


def get_me_ticket(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_me_ticket - start {timezone.now()}', '0')
    count_me = Ticket.object_role.c_me(request).exclude(organization_id=4).filter(
        status__status='open').count()
    if request.user.owner.role.role == 'engin':
        count_me = Ticket.object_role.c_me(request).filter(
            status__status='open', organization_id=4).count()
    listmeticket = Workflow.object_role.c_work_me(request).values('createdate').annotate(
        count=Count('id')).order_by('-createdate')[:5]

    # if request.user.is_superuser:
    #     add_to_log(request, f'get_me_ticket - end {timezone.now()}', '0')
    return count_me, sorted(listmeticket, key=itemgetter('createdate'), reverse=False)


def get_pending_ticket(request, _today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_pending_ticket - start {timezone.now()}', '0')
    try:
        openticket = Ticket.object_role.c_gs(request, 0).filter(status__status='open').exclude(
            organization_id=4).count()
        openticketyesterday = Ticket.object_role.c_gs(request, 0).exclude(organization_id=4).filter(
            status__status='open', create__date__year=_today.year,
            create__date__month=_today.month,
            create__date__day=_today.day).count()
        listopenticket = Ticket.object_role.c_gs(request, 0).values('shamsi_date').annotate(
            count=Count('id')).exclude(organization_id=4).order_by('-shamsi_date')[:5]
        # if request.user.is_superuser:
        #     add_to_log(request, f'get_pending_ticket - end {timezone.now()}', '0')
        return openticket, openticketyesterday, sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)
    except:
        return 0, 0, 0


def get_pending_ticket_engin(request, _today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_pending_ticket_engin - start {timezone.now()}', '0')
    openticket = Ticket.object_role.c_gs(request, 0).filter(status__status='open', organization_id=4).count()
    openticketyesterday = Ticket.object_role.c_gs(request, 0).filter(organization_id=4,
                                                                     status__status='open',
                                                                     create__date__year=_today.year,
                                                                     create__date__month=_today.month,
                                                                     create__date__day=_today.day).count()
    listopenticket = Ticket.object_role.c_gs(request, 0).values('shamsi_date').annotate(
        count=Count('id')).filter(organization_id=4).order_by('-shamsi_date')[:5]
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_pending_ticket_engin - end {timezone.now()}', '0')
    return openticket, openticketyesterday, sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)


def get_close_ticket(request, today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_close_ticket - start {timezone.now()}', '0')
    closeticket = Ticket.object_role.c_gs(request, 0).filter(
        closedate__year=today.year, closedate__month=today.month, closedate__day=today.day, status__status='close'
    ).count()
    listcloseticket = Ticket.object_role.c_gs(request, 0).values('close_shamsi_date').annotate(
        count=Count('id')).filter(status_id=2).order_by('-close_shamsi_date')[:5]
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_close_ticket - end {timezone.now()}', '0')
    return closeticket, sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)


def get_close_ticket_engin(request, today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_close_ticket_engin - start {timezone.now()}', '0')
    closeticket = Ticket.object_role.c_gs(request, 0).filter(
        closedate__year=today.year, closedate__month=today.month, closedate__day=today.day, status__status='close',
        actioner__role__role='engin',
    ).count()
    listcloseticket = Ticket.object_role.c_gs(request, 0).values('close_shamsi_date').annotate(
        count=Count('id')).filter(status_id=2, actioner__role__role='engin').order_by('-close_shamsi_date')[:5]
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_close_ticket_engin - end {timezone.now()}', '0')
    return closeticket, sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)


def get_newticketstatus(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_newticketstatus - start {timezone.now()}', '0')
    count_unit = Ticket.object_role.c_gs(request, 0).values('organization_id', 'organization__name').filter(
        status__status='open',
    ).annotate(tedad=Count('id')).order_by('-tedad')
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_newticketstatus - end {timezone.now()}', '0')
    return count_unit


def get_slider_items(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_slider_items - start {timezone.now()}', '0')
    rpm = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1164, status_id=1, is_system=True).count()
    napaydari = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1056, status_id=1, is_system=True).count()
    this_date = datetime.datetime.today()
    # datesell = SellModel.object_role.c_gs(request, 0).filter(
    #     tarikh=this_date - datetime.timedelta(days=1)).values(
    #     'gs_id').annotate(sellsum=Sum('sell'),
    #                       kolsum=Sum('sellkol'))
    gsmodel = GsModel.object_role.c_gsmodel(request).filter(status=1)
    subquery = SellModel.object_role.c_gs(request, 0).filter(
        gs_id=OuterRef('id'),
        tarikh=this_date - datetime.timedelta(days=1),
        sell__gte=0,
        sellkol__gte=0
    )

    nosell = gsmodel.annotate(
        has_sell=Exists(subquery)
    ).filter(has_sell=False).count()

    date_nosell1 = jdatetime.date.today() - datetime.timedelta(days=1)
    date_nosell = str(date_nosell1)[5:]
    date_nosell = date_nosell.replace("-", "/")
    gscount = GsModel.object_role.c_gsmodel(request).filter(active=True).count()
    nazelcount = Pump.object_role.c_gs(request, 0).filter(gs__active=True,
                                                          status__status=True).count()
    liststart = Ticket.object_role.c_gs(request, 0).filter(status__status='close',
                                                           star__gte=1, star__lte=5,
                                                           ).aggregate(
        star=Avg('star'), vote=Count('id'))
    if liststart['star']:
        stars = round(liststart['star'], 1)
    else:
        stars = 'امتیازی ثبت نشده'

    _today = date.today()

    napaydari_today = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        gs__active=True, create__date__year=_today.year, create__date__month=_today.month,
        create__date__day=_today.day,
        failure_id=1056, status_id=1, is_system=True).count()
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_slider_items - end {timezone.now()}', '0')
    return rpm, napaydari, date_nosell, nosell, gscount, nazelcount, stars, napaydari_today


def get_sla(request, _today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_sla - start {timezone.now()}', '0')
    statusmoavagh = StatusMoavagh.objects.all()
    two_ago_sell = _today.today() - datetime.timedelta(hours=48)
    sla = Ticket.object_role.c_gs(request, 0).exclude(organization_id=4).filter(create__lte=two_ago_sell,
                                                                                failure__failurecategory_id__in=[
                                                                                    1010, 1011],
                                                                                status_id=1,
                                                                                statusmoavagh_id__isnull=True).order_by(
        'id')[:10]
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_sla - end {timezone.now()}', '0')
    return sla, statusmoavagh


def get_alarms(request, _roleid):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_alarms - start {timezone.now()}', '0')
    alarms = TicketScience.object_role.c_gs(request, 0).order_by('-id')[:5]
    try:
        zonesetting = Zone.objects_limit.get(id=_roleid)
    except Zone.DoesNotExist:
        zonesetting = None
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_alarms - end {timezone.now()}', '0')
    return alarms, zonesetting


def get_forward_ticket(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_forward_ticket - start {timezone.now()}', '0')
    work = Workflow.object_role.c_ticket(request).order_by('-id')[:5]
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_forward_ticket - end {timezone.now()}', '0')
    return work


def get_napaydari_list(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_napaydari_list - start {timezone.now()}', '0')
    napaydari_list = Ticket.object_role.c_gs(request, 0).filter(
        status__status='open', gs__status__status=True,
        failure_id=1056, status_id=1, is_system=True)

    napydarilist = []

    for item in napaydari_list:

        tekname = GsList.objects.filter(owner__role__role='tek', gs_id=item.gs_id, owner__active=True).first()
        if tekname:
            teknameowner = tekname.owner
        else:
            teknameowner = 'نا مشخص'
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
            'tek': teknameowner,
            'rnd': item.rnd
        }
        napydarilist.append(_dict)

    # if request.user.is_superuser:
    #     add_to_log(request, f'get_napaydari_list - end {timezone.now()}', '0')
    return sorted(napydarilist, key=itemgetter('tedad'), reverse=True)


def get_store_counts(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_store_counts - start {timezone.now()}', '0')
    master_daghi = StoreList.object_role.c_base(request).filter(statusstore=1, status_id__in=[6, 10, 11]).count()
    pinpad_daghi = StoreList.object_role.c_base(request).filter(statusstore=2, status_id__in=[6, 10, 11]).count()
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_store_counts - end {timezone.now()}', '0')
    return master_daghi, pinpad_daghi


def get_arbain_pump_count(request, product_id):

    return Pump.object_role.c_gs(request, 0).filter(
        gs__arbain=True,
        gs__status__status=True,
        status__status=True,
        product_id=product_id
    ).count()


def get_arbain_ticket_count(request, product_id):
    return Ticket.object_role.c_gs(request, 0).exclude(organization_id=4).filter(
        gs__arbain=True,
        failure__failurecategory_id__in=[1010, 1011, 1045],
        Pump__product_id=product_id,
        status_id=1
    ).count()


def get_card(request):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_card - start {timezone.now()}', '0')
    cards = PanModels.object_role.c_gs(request, 0).filter(Q(statuspan_id=1) | Q(statuspan_id=2))

    card_expire_count = 0
    card_expire_area_count = 0

    for item in cards:
        if item.statuspan_id == 1 and item.expire_date() > 0:
            card_expire_count += 1
        elif item.statuspan_id == 2 and item.expire_date_area() > 0:
            card_expire_area_count += 1

    # if request.user.is_superuser:
    #     add_to_log(request, f'get_card - end {timezone.now()}', '0')
    return card_expire_count, card_expire_area_count


def get_statusstore(request, _today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_statusstore - start {timezone.now()}', '0')
    masters = StoreList.object_role.c_base(request).filter(status_id__in=[3, 4, 16], statusstore_id=1
                                                           ).count()
    store_takhsis = Store.object_role.c_base(request).filter(status_id=1,
                                                             ).aggregate(master=Sum('master'),
                                                                         pinpad=Sum('pinpad'))
    store_create_master = StoreList.object_role.c_base(request).filter(status_id=9,
                                                                       statusstore_id=1,
                                                                       ).count
    store_create_pinpad = StoreList.object_role.c_base(request).filter(status_id=9,
                                                                       statusstore_id=2,
                                                                       ).count

    store_noget = Store.object_role.c_base(request).filter(status_id=2,
                                                           ).aggregate(master=Sum('master'),
                                                                       pinpad=Sum('pinpad'))

    pinpads = StoreList.object_role.c_base(request).filter(status_id__in=[3, 4, 16], statusstore_id=2
                                                           ).count()
    count_master = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1010,
                                                              failure__isnazel=True).count()
    count_pinpad = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1011,
                                                              failure__isnazel=True).count()
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_statusstore - end {timezone.now()}', '0')
    return (masters, store_takhsis, store_create_master, store_create_pinpad,
            store_noget, pinpads, count_master, count_pinpad)


def get_workshop(request, _today):
    # if request.user.is_superuser:
    #     add_to_log(request, f'get_workshop - start {timezone.now()}', '0')
    store_workshop = Store.object_role.c_base(request).exclude(storage__refrence=False).filter(
        marsole_date__year=_today.year,
        marsole_date__month=_today.month,
        marsole_date__day=_today.day,
        status_id__in=[2, 3]
    ).aggregate(master=Sum('master'),
                pinpad=Sum('pinpad'))
    list_store_noget = Store.objects.values('storage__name').annotate(
        count=Sum('master') + Sum('pinpad')).exclude(storage__refrence=False).filter(marsole_date__year=_today.year,
                                                                                     status_id__in=[2, 3],
                                                                                     marsole_date__month=_today.month,
                                                                                     marsole_date__day=_today.day).order_by(
        '-count')

    # if request.user.is_superuser:
    #     add_to_log(request, f'get_workshop - end {timezone.now()}', '0')
    return store_workshop, list_store_noget
