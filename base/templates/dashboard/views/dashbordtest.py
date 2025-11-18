from django.db.models import Count, Sum, Q, Avg, Case, When
from operator import itemgetter
from base.models import Workflow, Ticket, GsList, Pump, GsModel, Area, Owner
from cart.models import PanModels
from pay.models import StoreList, Store
from sell.models import SellModel
from datetime import datetime, date
import jdatetime
from django.conf import settings
import datetime

unname = 'نا مشخص'


def dashboardtest(_refrenceid, _roleid, request):
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

    count_fani = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                organization_id=2,
                                                                ).count()
    count_test = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                organization_id=3,
                                                                ).count()

    napaydari = Ticket.object_role.c_gs(request,0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1056, status_id=1, is_system=True).count()
    rpm = Ticket.object_role.c_gs(request,0).values('gs_id').filter(
        status__status='open', gs__active=True,
        failure_id=1164, status_id=1, is_system=True).count()

    gscount = GsModel.object_role.c_gsmodel(request).filter(active=True).count()
    nazelcount = Pump.object_role.c_gs(request,0).filter(gs__active=True,
                                                              active=True).count()

    count_failure = Ticket.object_role.c_gs(request,0).values('failure_id', 'failure__info').filter(
        status__status='open', organization_id__in=[2, 3]).annotate(tedad=Count('id')).order_by('-tedad')

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
    this_date = datetime.datetime.today()
    gsmodel = GsModel.object_role.c_gsmodel(request).filter(active=True)
    nosell = gsmodel.exclude(
        id__in=SellModel.objects.filter(sell__gte=5, sellkol__gte=5,
                                        tarikh=this_date - datetime.timedelta(days=1)).values('gs_id')).count()
    date_nosell1 = jdatetime.date.today() - datetime.timedelta(days=1)
    date_nosell = str(date_nosell1)[5:]
    date_nosell = date_nosell.replace("-", "/")

    return ({'nosell': nosell, 'date_nosell': date_nosell,
             'listmeTicket': listmeticket,

             'listarea': listarea,
             'napaydari': napaydari,
             'card_expire_area_count': card_expire_area_count,
             'count_fani': count_fani,
             'sellamarlist': sellamarlist,
             'cards_expire': card_expire_count,
             'nazelcount': nazelcount, 'gscount': gscount, 'benzin_kol': benzin_kol,
             'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis,

             'listzone': listzone, 'list_gs': list_gs,
             'listnemodararea': listnemodararea, 'count_failure': count_failure,
             'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm,
             'count_test': count_test,
             })
