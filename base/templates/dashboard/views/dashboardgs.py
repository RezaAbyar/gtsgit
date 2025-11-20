from django.db.models import Count, Sum, Q, Avg, Case, When, Value, IntegerField
from operator import itemgetter
from base.models import Workflow, Ticket, GsList, Pump, GsModel, Area, Owner, Parametrs
from cart.models import PanModels
from pay.models import StoreList, Store
from sell.models import SellModel
from datetime import datetime, date
import jdatetime
from django.conf import settings
import datetime

unname = 'نا مشخص'


def dashboardgs(_refrenceid, _roleid, request):

    listmeticket = None
    benzin_kol = 0
    super_kol = 0
    gaz_kol = 0
    benzin_dis = 0
    super_dis = 0
    count_c_master = 0
    count_c_pinpad = 0
    gaz_dis = 0
    sellamarlist = []
    arbain = []
    list_gs = []
    listzone = []
    listnemodararea = []
    card_expire_count = 0
    card_expire_area_count = 0
    _today = date.today()
    listarea = []
    mygsid=GsList.objects.filter(owner_id=request.user.owner.id).first()




    openticket = Ticket.object_role.c_gs(request, 0).annotate(count=Count('id')).filter(
        status__status='open').exclude(organization_id=4)
    openticket = openticket.count()

    closeticket = Ticket.object_role.c_gs(request, 0).annotate(count=Count('id')).filter(
        closedate__year=_today.year,
        closedate__month=_today.month,
        closedate__day=_today.day,
        status__status='close')
    closeticket = closeticket.count()

    listcloseticket = Ticket.object_role.c_gs(request, 0).values('close_shamsi_date').annotate(
        count=Count('id')).filter(status_id=2).order_by(
        '-close_shamsi_date')[:5]

    try:
        listcloseticket = sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)
    except TypeError:
        listcloseticket = listcloseticket
    listopenticket = Ticket.object_role.c_gs(request, 0).values('shamsi_date').annotate(
        count=Count('id')).filter(
    ).exclude(organization_id=4).order_by('-shamsi_date')[:5]
    try:
        listopenticket = sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)
    except TypeError:
        listopenticket = listopenticket

    listmeticket = Workflow.object_role.c_work_me(request).values('createdate').annotate(
        count=Count('id')).order_by('-createdate')[:5]

    try:
        listmeticket = sorted(listmeticket, key=itemgetter('createdate'), reverse=False)
    except TypeError:
        listmeticket = listmeticket

    count_master = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1010,
                                                              failure__isnazel=True).count()
    count_pinpad = Ticket.object_role.c_gs(request, 0).filter(status__status='open',
                                                              failure__failurecategory_id=1011,
                                                              failure__isnazel=True).count()

    napaydari = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1056, status_id=1, is_system=True).count()
    rpm = Ticket.object_role.c_gs(request, 0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1164, status_id=1, is_system=True).count()

    openticketyesterday = Ticket.object_role.c_gs(request, 0).exclude(organization_id=4).filter(

        status__status='open', create__date__year=_today.year,
        create__date__month=_today.month,
        create__date__day=_today.day).count()

    star = Ticket.object_role.c_gs(request, 0).filter(status_id=2, star=0)
    liststart = Ticket.object_role.c_gs(request, 0).filter(status__status='close',
                                                           star__gte=1, star__lte=5,
                                                           ).aggregate(
        star=Avg('star'), vote=Count('id'))
    if liststart['star']:
        stars = round(liststart['star'], 1)
    else:
        stars = 'امتیازی ثبت نشده'


    _today = date.today()


    count_me = Ticket.object_role.c_me(request).filter(status__status='close').count()
    count_c_master = Ticket.object_role.c_me(request).filter(status__status='close',
                                                             reply_id__in=[2, 4, 57, 58, 59, 60]).count()
    count_c_pinpad = Ticket.object_role.c_me(request).filter(status__status='close',
                                                             reply_id__in=[3, 4, 57, 58, 61, 62]).count()
    parametr = Parametrs.objects.all().first()
    return ({'openticket': openticket, 'closeticket': closeticket, 'count_c_master': count_c_master,
             'count_c_pinpad': count_c_pinpad,'parametr':parametr,
             'openticketyesterday': openticketyesterday, 'listmeTicket': listmeticket,
             'listCloseTicket': listcloseticket, 'star': star,
             'listOpenTicket': listopenticket,
             'listarea': listarea,'mygsid':mygsid,
             'count_master': count_master, 'napaydari': napaydari,
             'count_me': count_me, 'card_expire_area_count': card_expire_area_count,
             'count_pinpad': count_pinpad,
             'sellamarlist': sellamarlist,
             'cards_expire': card_expire_count,
             'benzin_kol': benzin_kol,
             'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis,
             'listzone': listzone, 'list_gs': list_gs, 'listnemodararea': listnemodararea,
             'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm,
             'stars': stars,
             })
