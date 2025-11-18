import os
import django
from base.models import GsModel, Zone, Pump, Ticket, DailyTicketsReport
from util import SUM_TITEL


def my_function():
    _list = []
    zone = Zone.objects_limit.all().exclude(id=9).order_by('id')
    s_master = 0
    s_pinpad = 0
    summ = 0
    sum_gs = 0
    sum_pump = 0
    sum_ticket = 0
    sum_master = 0
    sum_pinpad = 0

    for gs in zone:
        count_gs = GsModel.objects.filter(area__zone_id=gs.id, status__status=True).count()
        count_pump = Pump.objects.filter(gs__area__zone_id=gs.id, status__status=True,
                                         gs__status__status=True).count()
        count_ticket = Ticket.objects.exclude(organization_id=4).filter(gs__area__zone_id=gs.id, status_id=1,
                                                                        gs__status__status=True,
                                                                        Pump__status__status=True,
                                                                        failure__failurecategory_id__in=[1010,
                                                                                                         1011]).count()

        count_master = Ticket.objects.exclude(organization_id=4).filter(gs__area__zone_id=gs.id, status_id=1,
                                                                        gs__status__status=True,
                                                                        Pump__status__status=True,
                                                                        failure__failurecategory_id=1010,
                                                                        failure__isnazel=True).count()

        count_pinpad = Ticket.objects.exclude(organization_id=4).filter(gs__area__zone_id=gs.id, status_id=1,
                                                                        gs__status__status=True,
                                                                        Pump__status__status=True,
                                                                        failure__failurecategory_id=1011,
                                                                        failure__isnazel=True).count()
        if count_master > 0:
            master = ((int(count_master) / int(count_pump)) * 100)
        else:
            master = 0
        if count_pinpad > 0:
            pinpad = ((int(count_pinpad) / int(count_pump)) * 100)
        else:
            pinpad = 0
        summ = round(master + pinpad, 2)
        DailyTicketsReport.objects.create(zone_id=gs.id,name=gs.name, count_ticket=count_ticket, summ=summ,
                                          count_master=count_master,
                                          count_pinpad=count_pinpad, master=round(master, 2),
                                          pinpad=round(pinpad, 2), count_pump=count_pump, count_gs=count_gs)

        sum_gs += count_gs
        sum_pump += count_pump
        sum_ticket += count_ticket
        sum_master += count_master
        sum_pinpad += count_pinpad
        if sum_master > 0:
            s_master = ((int(sum_master) / int(sum_pump)) * 100)
        else:
            s_master = 0
        if count_pinpad > 0:
            s_pinpad = ((int(sum_pinpad) / int(sum_pump)) * 100)
        else:
            s_pinpad = 0
        summ = round(s_master + s_pinpad, 2)

    DailyTicketsReport.objects.create(st=1, name=SUM_TITEL, count_ticket=sum_ticket, summ=summ, count_master=sum_master,
                                      count_pinpad=sum_pinpad, master=round(s_master, 2),
                                      pinpad=round(s_pinpad, 2), count_pump=sum_pump, count_gs=sum_gs)


