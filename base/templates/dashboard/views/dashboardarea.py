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
from django.utils import timezone
from datetime import timedelta

unname = 'نا مشخص'


def dashboardarea(_refrenceid, _roleid, request):
    listmeticket = None
    benzin_kol = 0
    super_kol = 0
    gaz_kol = 0
    benzin_dis = 0
    super_dis = 0
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
    bn1 = 0
    bn2 = 0
    bn3 = 0
    bn11 = 0
    bn12 = 0
    gn1 = 0
    gn3 = 0
    gn11 = 0

    ten_days_ago = timezone.now() - timedelta(days=15)
    cartarea = PanModels.object_role.c_gs(request, 0).filter(statuspan_id=2).count()
    cartgs = PanModels.object_role.c_gs(request, 0).filter(statuspan_id=1).count()

    moghayerat = SellModel.object_role.c_gs(request, 0).filter(
        tarikh=datetime.date.today() - datetime.timedelta(days=1),
        nomojaz__gte=5).count()

    cards_expire = PanModels.object_role.c_gs(request, 0).filter(statuspan_id=1)
    for item in cards_expire:
        if item.expire_date() > 0:
            card_expire_count += 1

    cards_expire_area = PanModels.object_role.c_gs(request, 0).filter(statuspan_id=2)
    for item in cards_expire_area:
        if item.expire_date_area() > 0:
            card_expire_area_count += 1

    work = Workflow.object_role.c_ticket(request).order_by('-id')[:9]

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

    listcloseticket = sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)

    listopenticket = Ticket.object_role.c_gs(request, 0).values('shamsi_date').annotate(
        count=Count('id')).filter(
    ).exclude(organization_id=4).order_by('-shamsi_date')[:5]
    listopenticket = sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)

    listmeticket = Workflow.object_role.c_work_me(request).values('createdate').annotate(
        count=Count('id')).order_by('-createdate')[:5]
    listmeticket = sorted(listmeticket, key=itemgetter('createdate'), reverse=False)

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

    ten_ago_sell = _today.today() - datetime.timedelta(days=10)
    sellamarlist = SellModel.object_role.c_gs(request, 0).values('tarikh').filter(
        tarikh__gte=ten_ago_sell,
        tarikh__lte=_today.today()).annotate(
        bn1=((Sum(Case(When(product_id=2, then='yarane'), default=Value(0),
                       output_field=IntegerField())) / (Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),

        bn2=((Sum(Case(When(product_id=2, then='azad'), default=Value(0),
                       output_field=IntegerField())) / (Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),

        bn3=((Sum(Case(When(product_id=2, then='ezterari'), default=Value(0),
                       output_field=IntegerField())) / (Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),
        bn11=((Sum(Case(When(product_id=2, then='yarane'), default=Value(0),
                        output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField()))) / (Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0),
                 output_field=IntegerField()))) * 100),
        bn12=((Sum(Case(When(product_id=2, then='ezterari'), default=Value(0),
                        output_field=IntegerField())) / (Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),
        sum=Sum(
            Case(When(product_id=2, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=2, then='ezterari'), default=Value(0), output_field=IntegerField())),

        gn1=((Sum(Case(When(product_id=4, then='yarane'), default=Value(0),
                       output_field=IntegerField())) / (Sum(
            Case(When(product_id=4, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),
        gn3=((Sum(Case(When(product_id=4, then='ezterari'), default=Value(0),
                       output_field=IntegerField())) / (Sum(
            Case(When(product_id=4, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),
        gn11=((Sum(Case(When(product_id=4, then='yarane'), default=Value(0),
                        output_field=IntegerField())) + (Sum(
            Case(When(product_id=4, then='azad'), default=Value(0), output_field=IntegerField())) / Sum(
            Case(When(product_id=4, then='yarane'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='azad'), default=Value(0), output_field=IntegerField())) + Sum(
            Case(When(product_id=4, then='ezterari'), default=Value(0),
                 output_field=IntegerField())))) * 100),

    ).order_by(
        'tarikh')

    count_me = Ticket.object_role.c_me(request).exclude(organization_id=4).filter(
        status__status='open').count()

    _today = date.today()
    isarbain = Parametrs.objects.get(id=1)
    _is_arbain = isarbain.is_arbain

    if _is_arbain:
        benzin_kol = Pump.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, status_id=1,
                                                              product_id=2
                                                              ).count()
        super_kol = Pump.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, status_id=1,
                                                             product_id=3
                                                             ).count()
        gaz_kol = Pump.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, status_id=1,
                                                           product_id=4
                                                           ).count()
        benzin_dis = Ticket.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, Pump__status_id=1,
                                                                Pump__product_id=2,
                                                                status_id=1).count()
        super_dis = Ticket.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, Pump__status_id=1,
                                                               Pump__product_id=3,
                                                               status_id=1).count()
        gaz_dis = Ticket.object_role.c_gs(request, 0).filter(gs__arbain=True, gs__status_id=1, Pump__status_id=1,
                                                             Pump__product_id=4,
                                                             status_id=1, ).count()

        result = SellModel.object_role.c_gs(request, 0).values('tarikh').filter(tarikh__gte=ten_days_ago,
                                                                                tarikh__lte=_today.today(),
                                                                                gs__arbain=True).annotate(
            n1=Sum('yarane'),
            n2=Sum('azad'),
            n3=Sum('ezterari'),
            sum=Sum('yarane') + Sum(
                'azad') + Sum(
                'ezterari')).order_by(
            'tarikh')
        arbain = []
        if result:
            for sell in result:
                _dict = {
                    'name': str(sell['tarikh']),
                    'n1': round(sell['n1']),
                    'n2': round(sell['n2']),
                    'n3': round(sell['n3']),
                }
                arbain.append(_dict)
    this_date = datetime.datetime.today()
    gscount = GsModel.object_role.c_gsmodel(request).filter(active=True).count()
    nazelcount = Pump.object_role.c_gs(request, 0).filter(gs__active=True,
                                                          active=True).count()
    datesell = SellModel.object_role.c_gs(request, 0).filter(tarikh=this_date - datetime.timedelta(days=1)).values(
        'gs_id').annotate(sellsum=Sum('sell'),
                          kolsum=Sum('sellkol'))
    gsmodel = GsModel.object_role.c_gsmodel(request).filter(status=1)

    nosell = gsmodel.exclude(
        id__in=datesell.filter(sellsum__gte=0, kolsum__gte=0).values('gs_id')).count()
    date_nosell1 = jdatetime.date.today() - datetime.timedelta(days=1)
    date_nosell = str(date_nosell1)[5:]
    date_nosell = date_nosell.replace("-", "/")

    listowner = []
    for area in Owner.object_role.c_base(request).filter(role__role='tek', active=True):
        listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
                                                 gs__gsowner__owner_id=area.id).count()
        listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
                                                 gs__gsowner__owner_id=area.id).count()
        listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
                                                status__status='open',
                                                gs__gsowner__owner_id=area.id).count()
        dictarea = {
            'area': str(area.name) + ' ' + str(area.lname),
            'listMasterTicket': listmasterticket,
            'listPinpadTicket': listpinpadticket,
            'listOtherTicket': listotherticket,
            'sum': int(listmasterticket) + int(listpinpadticket) + int(listotherticket),
        }
        listowner.append(dictarea)
        listowner = sorted(listowner, key=itemgetter('sum'), reverse=True)
        listowner = listowner[:10]

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

    if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
        listmasterticket = Ticket.objects.values('gs__area__zone__name').filter(
            failure__failurecategory_id__in=[1010, 1011], status__status='open',
        ).annotate(m=Count('id')).order_by('-m')[:10]

        for item in listmasterticket:
            dictarea = {
                'area': str(item['gs__area__zone__name']),
                'listMasterTicket': item['m'],
            }
            listzone.append(dictarea)

        listmasterticket = Ticket.objects.values('gs__area_id', 'gs__area__name', 'gs__area__zone__name').filter(
            failure__failurecategory_id__in=[1010, 1011], status__status='open',
        ).annotate(m=Count('id')).order_by('-m')[:10]

        for item in listmasterticket:
            dictarea = {
                'area': str(item['gs__area__name']) + "(" + str(item['gs__area__zone__name']) + ")",
                'listMasterTicket': item['m'],
            }
            listnemodararea.append(dictarea)

        listmasterticket = Ticket.objects.values('gs_id', 'gs__name', 'gs__area__name',
                                                 'gs__area__zone__name').filter(
            failure__failurecategory_id__in=[1010, 1011], status__status='open',
        ).annotate(m=Count('id')).order_by('-m')[:10]

        for item in listmasterticket:
            dictarea = {
                'area': str(item['gs__name']) + "(" + str(item['gs__area__name']) + " - " + str(
                    item['gs__area__zone__name']) + ")",
                'listMasterTicket': item['m'],
            }
            list_gs.append(dictarea)

    return ({'openticket': openticket, 'closeticket': closeticket,
             'openticketyesterday': openticketyesterday, 'listmeTicket': listmeticket,
             'listCloseTicket': listcloseticket, 'listgs': listgs, 'listowner': listowner,
             'listOpenTicket': listopenticket, 'napaydari_today': napaydari_today,
             'listarea': listarea, 'moghayerat': moghayerat,
             'count_master': count_master, 'napaydari': napaydari, 'nosell': nosell,
             'date_nosell': str(date_nosell), 'count_me': count_me, 'card_expire_area_count': card_expire_area_count,
             'count_pinpad': count_pinpad, 'count_fani': count_fani, 'count_engin': count_engin, 'count_gs': count_gs,
             'sellamarlist': sellamarlist, 'cartarea': cartarea, 'cartgs': cartgs,
             'cards_expire': card_expire_count, 'count_area': count_area,
             'nazelcount': nazelcount, 'gscount': gscount, 'benzin_kol': benzin_kol,
             'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis,
             'listzone': listzone, 'list_gs': list_gs, 'listnemodararea': listnemodararea,
             'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm,
             'count_test': count_test, 'count_tek': count_tek, 'stars': stars,
             'work': work, 'napaydari_list': napydarilist})
