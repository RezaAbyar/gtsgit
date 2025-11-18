# from django.db.models import Count, Sum, Q, Avg
# from datetime import date
# from operator import itemgetter
# from base.models import Workflow, Ticket, GsList, Pump, GsModel, Area, Owner
# from cart.models import PanModels
# from pay.models import StoreList, Store
# from sell.models import SellModel
# from datetime import datetime, date
# import jdatetime
# from django.conf import settings
# import datetime
#
# unname = 'نا مشخص'
#
#
# def dashboardzone(_zoneid, _a, _refrenceid):
#     listarea = []
#     card_expire_count = 0
#     a = _a
#     _today = date.today()
#     cards_expire = PanModels.objects.filter(statuspan_id=1, gs__area__zone_id=_zoneid)
#     for item in cards_expire:
#         if item.expire_date() > 0:
#             card_expire_count += 1
#
#     work = Workflow.objects.filter(ticket__gs__area__zone_id=_zoneid).order_by('-id')[:9]
#     openticket = Ticket.objects.annotate(count=Count('id')).filter(
#         gs__area__zone_id=_zoneid,
#         status__status='open').exclude(organization_id=4)
#     openticket = openticket.count()
#     closeticket = Ticket.objects.annotate(count=Count('id')).filter(closedate__year=_today.year,
#                                                                     closedate__month=_today.month,
#                                                                     closedate__day=_today.day,
#                                                                     gs__area__zone_id=_zoneid,
#                                                                     status__status='close')
#     closeticket = closeticket.count()
#     listcloseticket = Ticket.objects.values('close_shamsi_date').annotate(
#         count=Count('id')).filter(gs__area__zone_id=_zoneid, status_id=2).order_by(
#         '-close_shamsi_date')[:5]
#     listcloseticket = sorted(listcloseticket, key=itemgetter('close_shamsi_date'), reverse=False)
#
#     listopenticket = Ticket.objects.values('shamsi_date').annotate(
#         count=Count('id')).filter(
#         gs__area__zone_id=_zoneid
#     ).exclude(organization_id=4).order_by('-shamsi_date')[
#                      :5]
#     listopenticket = sorted(listopenticket, key=itemgetter('shamsi_date'), reverse=False)
#     if _refrenceid == 1:
#         listmeticket = Workflow.objects.values('createdate').annotate(count=Count('id')).filter(
#             ticket__gs__area__zone_id=_zoneid, organization_id=5,
#         ).order_by('-createdate')[:5]
#         listmeticket = sorted(listmeticket, key=itemgetter('createdate'), reverse=False)
#     master_daghi = StoreList.objects.filter(zone_id=_zoneid, statusstore=1,
#                                             status_id__in=[6, 10, 11]).count()
#     pinpad_daghi = StoreList.objects.filter(zone_id=_zoneid, statusstore=2,
#                                             status_id__in=[6, 10, 11]).count()
#     masters = StoreList.objects.filter(status_id__in=[3, 4], statusstore_id=1,
#                                        zone_id=_zoneid).count()
#     store_takhsis = Store.objects.filter(zone_id=_zoneid, status_id__in=[1, 9],
#                                          ).aggregate(master=Sum('master'), pinpad=Sum('pinpad'))
#     store_create_master = StoreList.objects.filter(zone_id=_zoneid, status_id=9,
#                                                    statusstore_id=1,
#                                                    ).count
#     store_create_pinpad = StoreList.objects.filter(zone_id=_zoneid, status_id=9,
#                                                    statusstore_id=2,
#                                                    ).count
#     store_noget = Store.objects.filter(zone_id=_zoneid, status_id=2,
#                                        ).aggregate(master=Sum('master'), pinpad=Sum('pinpad'))
#     pinpads = StoreList.objects.filter(status_id__in=[3, 4], statusstore_id=2,
#                                        zone_id=_zoneid).count()
#     count_master = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                          failure__failurecategory_id=1010,
#                                          failure__isnazel=True).count()
#     count_pinpad = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                          failure__failurecategory_id=1011,
#                                          failure__isnazel=True).count()
#     count_fani = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                        organization_id=2,
#                                        ).count()
#     count_test = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                        organization_id=3,
#                                        ).count()
#     count_engin = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                         organization_id=4,
#                                         ).count()
#     count_tek = Ticket.objects.filter(gs__area__zone_id=_zoneid, status__status='open',
#                                       organization_id=1,
#                                       ).count()
#     napaydari = Ticket.objects.values('gs_id').filter(gs__area__zone_id=_zoneid,
#                                                       status__status='open', gs__status__status=True,
#                                                       failure_id=1056, status_id=1, is_system=True).count()
#     rpm = Ticket.objects.values('gs_id').filter(gs__area__zone_id=_zoneid,
#                                                 status__status='open', gs__status__status=True,
#                                                 failure_id=1164, status_id=1, is_system=True).count()
#     napaydari_list = Ticket.objects.filter(gs__area__zone_id=_zoneid,
#                                            status__status='open', gs__status__status=True,
#                                            failure_id=1056, status_id=1, is_system=True)
#     openticketyesterday = Ticket.objects.exclude(organization_id=4).filter(
#         gs__area__zone_id=_zoneid,
#         status__status='open', create__date__year=_today.year,
#         create__date__month=_today.month,
#         create__date__day=_today.day).count()
#
#     napydarilist = []
#     liststart = Ticket.objects.filter(status__status='close', gs__area__zone_id=_zoneid,
#                                       star__gte=1, star__lte=5,
#                                       ).aggregate(
#         star=Avg('star'), vote=Count('id'))
#
#     if liststart['star']:
#         stars = round(liststart['star'], 1)
#     else:
#         stars = 'امتیازی ثبت نشده'
#     for item in napaydari_list:
#
#         tekname = GsList.objects.filter(owner__role__role='tek', gs_id=item.gs_id, owner__active=True).first()
#         if tekname:
#             teknameowner = tekname.owner
#         else:
#             teknameowner = unname
#         today = datetime.datetime.today()
#         t1 = date(year=today.year, month=today.month, day=today.day)
#         outdate = item.create
#         t2 = date(year=outdate.year, month=outdate.month, day=outdate.day)
#         tedad = (t1 - t2).days
#         _dict = {
#             'id': item.id,
#             'gsid': item.gs.gsid,
#             'name': item.gs.name,
#             'nahye': item.gs.area.name,
#             'tedad': tedad,
#             'tek': teknameowner
#         }
#         napydarilist.append(_dict)
#     napydarilist = sorted(napydarilist, key=itemgetter('tedad'), reverse=True)
#     _today = date.today()
#     if settings.IS_ARBAIN == True:
#         benzin_kol = Pump.objects.filter(gs__arbain=True, gs__active=True, active=True, product_id=2,
#                                          gs__area__zone_id=_zoneid).count()
#         super_kol = Pump.objects.filter(gs__arbain=True, gs__active=True, active=True, product_id=3,
#                                         gs__area__zone_id=_zoneid).count()
#         gaz_kol = Pump.objects.filter(gs__arbain=True, gs__active=True, active=True, product_id=4,
#                                       gs__area__zone_id=_zoneid).count()
#         benzin_dis = Ticket.objects.filter(gs__arbain=True, gs__active=True, Pump__active=True, Pump__product_id=2,
#                                            status_id=1,
#                                            gs__area__zone_id=_zoneid).count()
#         super_dis = Ticket.objects.filter(gs__arbain=True, gs__active=True, Pump__active=True, Pump__product_id=3,
#                                           status_id=1,
#                                           gs__area__zone_id=_zoneid).count()
#         gaz_dis = Ticket.objects.filter(gs__arbain=True, gs__active=True, Pump__active=True, Pump__product_id=4,
#                                         status_id=1,
#                                         gs__area__zone_id=_zoneid).count()
#
#         result = SellModel.objects.values('tarikh').filter(tarikh__gte='2023-08-15', tarikh__lte=_today.today(),
#                                                            gs__arbain=True,
#                                                            gs__area__zone_id=_zoneid).annotate(
#             n1=Sum('yarane'),
#             n2=Sum('azad'),
#             n3=Sum('ezterari'),
#             sum=Sum('yarane') + Sum(
#                 'azad') + Sum(
#                 'ezterari')).order_by(
#             'tarikh')
#         arbain = []
#         if result:
#             for sell in result:
#                 _dict = {
#                     'name': str(sell['tarikh']),
#                     'n1': round(sell['n1']),
#                     'n2': round(sell['n2']),
#                     'n3': round(sell['n3']),
#                 }
#                 arbain.append(_dict)
#     this_date = datetime.datetime.today()
#     gscount = GsModel.objects.filter(area__zone_id=_zoneid, active=True).count()
#     nazelcount = Pump.objects.filter(gs__area__zone_id=_zoneid, gs__active=True,
#                                      active=True).count()
#     gsmodel = GsModel.objects.filter(area__zone_id=_zoneid, active=True)
#     nosell = gsmodel.exclude(
#         id__in=SellModel.objects.filter(sell__gte=5, sellkol__gte=5,tarikh=this_date - datetime.timedelta(days=1)).values('gs_id')).count()
#     date_nosell1 = jdatetime.date.today() - datetime.timedelta(days=1)
#     date_nosell = str(date_nosell1)[5:]
#     date_nosell = date_nosell.replace("-", "/")
#
#     for area in Area.objects.filter(zone_id=_zoneid):
#         listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
#                                                  gs__area_id=area.id).count()
#         listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
#                                                  gs__area_id=area.id).count()
#         listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
#                                                 status__status='open',
#                                                 gs__area_id=area.id).count()
#         dictarea = {
#             'area': str(area.name),
#             'listMasterTicket': listmasterticket,
#             'listPinpadTicket': listpinpadticket,
#             'listOtherTicket': listotherticket
#         }
#         listarea.append(dictarea)
#     if a == 'tek':
#
#         listarea = []
#         for area in Owner.objects.filter(zone_id=_zoneid, role__role='tek', active=True):
#             listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
#                                                      gs__gsowner__owner_id=area.id).count()
#             listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
#                                                      gs__gsowner__owner_id=area.id).count()
#             listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
#                                                     status__status='open',
#                                                     gs__gsowner__owner_id=area.id).count()
#             dictarea = {
#                 'area': str(area.name) + ' ' + str(area.lname),
#                 'listMasterTicket': listmasterticket,
#                 'listPinpadTicket': listpinpadticket,
#                 'listOtherTicket': listotherticket
#             }
#             listarea.append(dictarea)
#
#     if a == 'gs':
#         listarea = []
#         for area in GsModel.objects.filter(area__zone_id=_zoneid):
#             listmasterticket = Ticket.objects.filter(failure__failurecategory_id=1010, status__status='open',
#                                                      gs_id=area.id).count()
#             listpinpadticket = Ticket.objects.filter(failure__failurecategory_id=1011, status__status='open',
#                                                      gs_id=area.id).count()
#             listotherticket = Ticket.objects.filter(~Q(failure__failurecategory_id__in=[1010, 1011]),
#                                                     status__status='open',
#                                                     gs_id=area.id).count()
#             dictarea = {
#                 'area': str(area.name) + ' ' + str(area.gsid),
#                 'listMasterTicket': listmasterticket,
#                 'listPinpadTicket': listpinpadticket,
#                 'listOtherTicket': listotherticket,
#                 'sum': int(listmasterticket) + int(listpinpadticket) + int(listotherticket),
#             }
#             listarea.append(dictarea)
#         listarea = sorted(listarea, key=itemgetter('sum'), reverse=True)
#         listarea = listarea[:10]
#
#         return ({'openticket': openticket, 'closeticket': closeticket,
#                  'a': a,
#                  'openticketyesterday': openticketyesterday, 'listmeTicket': listmeticket,
#                  'listCloseTicket': listcloseticket,
#                  'listOpenTicket': listopenticket,
#                  'listarea': listarea, 'masters': masters, 'pinpads': pinpads,
#                  'count_master': count_master, 'napaydari': napaydari, 'nosell': nosell,
#                  'date_nosell': str(date_nosell),
#                  'count_pinpad': count_pinpad, 'count_fani': count_fani, 'count_engin': count_engin,
#                  'store_takhsis': store_takhsis,
#                  'cards_expire': card_expire_count,
#                  'store_noget': store_noget, 'nazelcount': nazelcount, 'gscount': gscount, 'benzin_kol': benzin_kol,
#                  'super_kol': super_kol, 'gaz_kol': gaz_kol, 'benzin_dis': benzin_dis, 'master_daghi': master_daghi,
#                  'pinpad_daghi': pinpad_daghi, 'store_create_master': store_create_master,
#                  'store_create_pinpad': store_create_pinpad,
#                  'super_dis': super_dis, 'gaz_dis': gaz_dis, 'arbain': arbain, 'rpm': rpm,
#                  'count_test': count_test, 'count_tek': count_tek, 'stars': stars,
#                  'work': work, 'napaydari_list': napydarilist})
