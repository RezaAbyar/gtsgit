import time
from django.db.models import Count, Sum
from base.models import Ticket, Parametrs
from pay.models import StoreList, Store
from sell.models import SellModel
from datetime import date
from django.utils import timezone
from .dashboarditems import get_sla, get_card, get_alarms, get_workshop, get_statusstore, get_newticketstatus, \
    get_store_counts, get_arbain_pump_count, get_arbain_ticket_count, get_me_ticket , get_forward_ticket, \
    get_slider_items, get_napaydari_list, get_close_ticket ,get_pending_ticket
from datetime import timedelta

def dashboardzone(_refrenceid, _roleid, request):
    from django.db import connection
    import traceback
    connection.queries_log.clear()
    start_time = time.time()
    benzin_kol = 0
    super_kol = 0
    gaz_kol = 0
    benzin_dis = 0
    super_dis = 0
    gaz_dis = 0
    sellamarlist = []
    arbain = []
    list_gs = []
    listgs = []
    listowner = []
    listzone = []
    master_daghi = pinpad_daghi = masters = store_takhsis = store_create_master = store_create_pinpad = store_noget = store_workshop = list_store_noget = pinpads = count_master = count_pinpad = 0
    listnemodararea = []
    _today = date.today()
    _today2 = time.time()
    listarea = []
    moghayerat = 0
    today = timezone.now().date()
    _today = date.today()
    card_expire_count = 0
    card_expire_area_count = 0
    ten_days_ago = timezone.now() - timedelta(days=15)
    if request.user.owner.role.role in ['zone', 'tek']:
        master_daghi, pinpad_daghi = get_store_counts(request)

    count_me, listmeticket = get_me_ticket(request)
    rpm, napaydari, date_nosell, nosell, gscount, nazelcount, stars, napaydari_today = get_slider_items(request)
    openticket, openticketyesterday, listopenticket = get_pending_ticket(request, _today)
    closeticket, listcloseticket = get_close_ticket(request, today)
    sla, statusmoavagh = get_sla(request, _today)
    alarms, zonesetting = get_alarms(request, _roleid)
    work = get_forward_ticket(request)
    count_unit = get_newticketstatus(request)
    napydarilist = get_napaydari_list(request)

    if request.user.owner.role.role in ['mgr', 'setad', 'fani']:
        store_workshop, list_store_noget = get_workshop(request, _today)
    if request.user.owner.role.role in ['zone', 'area']:
        card_expire_count, card_expire_area_count = get_card(request)

    if request.user.owner.role.role in ['zone', 'tek']:
        (masters, store_takhsis, store_create_master,
         store_create_pinpad, store_noget, pinpads, count_master, count_pinpad) = get_statusstore(
            request, _today)

    isarbain = Parametrs.objects.get(id=1)
    _is_arbain = isarbain.is_arbain

    if _is_arbain:
        benzin_kol = get_arbain_pump_count(request, product_id=2)
        super_kol = get_arbain_pump_count(request, product_id=3)
        gaz_kol = get_arbain_pump_count(request, product_id=4)
        benzin_dis = get_arbain_ticket_count(request, product_id=2)
        super_dis = get_arbain_ticket_count(request, product_id=3)
        gaz_dis = get_arbain_ticket_count(request, product_id=4)

        result = SellModel.object_role.c_gs(request, 0).values('tarikh').filter(tarikh__gte=ten_days_ago,
                                                                                tarikh__lte=_today.today(),
                                                                                gs__arbain=True).annotate(
            n1=Sum('yarane', default=0),
            n2=Sum('azad', default=0),
            n3=Sum('ezterari', default=0),
            sum=Sum('yarane', default=0) + Sum(
                'azad', default=0) + Sum(
                'ezterari', default=0)).order_by(
            'tarikh')
        arbain = []
        if result.exists():
            arbain = [
                {
                    'name': str(sell['tarikh']),
                    'n1': round(sell['n1']),
                    'n2': round(sell['n2']),
                    'n3': round(sell['n3']),
                }
                for sell in result
            ]

    if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
        listmasterticket = Ticket.objects.values('gs__area__zone__name', 'gs__area__zone_id').filter(
            failure__failurecategory_id__in=[1010, 1011], status__status='open',
        ).annotate(m=Count('id')).order_by('-m')[:37]

        for item in listmasterticket:
            storecount = StoreList.objects.filter(zone_id=item['gs__area__zone_id'], status_id__in=[3, 4]).count()
            dictarea = {
                'area': str(item['gs__area__zone__name']),
                'listMasterTicket': item['m'],
                'storecount': storecount,
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

    # print("\n" + "=" * 100)
    # print("DETAILED QUERY ANALYSIS WITH SOURCE")
    # print("=" * 100)

    # for i, query in enumerate(connection.queries):
    #     query_time = float(query['time'])
    #
    #     # پیدا کردن منشاء کوئری از stack trace
    #     stack = traceback.extract_stack()
    #     source_info = "Unknown"
    #     for frame in stack[:-5]:  # حذف فریم‌های مربوط به خود این تابع
    #         if 'dashboarditems.py' in frame.filename:
    #             source_info = f"{frame.filename}:{frame.lineno} - {frame.name}"
    #             break
    #
    #     status = "SLOW" if query_time > 0.1 else "OK" if query_time > 0.05 else "FAST"

        # print(f"{i + 1:2d}. {query_time:6.3f}s {status}")
        # print(f"     Source: {source_info}")
        # print(f"     SQL: {query['sql'][:80]}...")
        # print()

    # total_time = time.time() - start_time
    # print(f"Total execution time: {total_time:.3f}s")

    return ({'openticket': openticket, 'closeticket': closeticket,
             'openticketyesterday': openticketyesterday, 'listmeTicket': listmeticket,
             'listCloseTicket': listcloseticket, 'listgs': listgs, 'listowner': listowner,
             'listOpenTicket': listopenticket, 'napaydari_today': napaydari_today,
             'listarea': listarea, 'masters': masters, 'pinpads': pinpads, 'moghayerat': moghayerat,
             'count_master': count_master, 'napaydari': napaydari, 'nosell': nosell,
             'date_nosell': str(date_nosell), 'count_me': count_me, 'card_expire_area_count': card_expire_area_count,
             'count_pinpad': count_pinpad,
             'store_takhsis': store_takhsis, 'sellamarlist': sellamarlist,
             'cards_expire': card_expire_count, 'store_workshop': store_workshop, 'list_store_noget': list_store_noget,
             'store_noget': store_noget, 'nazelcount': nazelcount, 'gscount': gscount, 'benzin_kol': benzin_kol,
             'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis, 'master_daghi': master_daghi,
             'pinpad_daghi': pinpad_daghi, 'store_create_master': store_create_master,
             'store_create_pinpad': store_create_pinpad, 'listzone': listzone, 'list_gs': list_gs,
             'listnemodararea': listnemodararea, 'statusmoavagh': statusmoavagh,
             'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm, 'zonesetting': zonesetting,
             'stars': stars, 'alarms': alarms, 'sla': sla, 'count_unit': count_unit,
             'work': work, 'napaydari_list': napydarilist})
