import time
from datetime import date
from django.utils import timezone
from .dashboarditems import get_newticketstatus, get_me_ticket, \
    get_slider_items, get_napaydari_list, get_close_ticket_engin, get_pending_ticket_engin


def dashboardzone(_refrenceid, _roleid, request):
    _today = date.today()
    _today2 = time.time()
    today = timezone.now().date()
    _today = date.today()
    try:
        count_me, listmeticket = get_me_ticket(request)
        openticket, openticketyesterday, listopenticket = get_pending_ticket_engin(request, _today)
        closeticket, listcloseticket = get_close_ticket_engin(request, today)
        count_unit = get_newticketstatus(request)
        napydarilist = get_napaydari_list(request)
        rpm, napaydari, date_nosell, nosell, gscount, nazelcount, stars, napaydari_today = get_slider_items(request)
    except:

        return False

    return {'count_me': count_me, 'listmeticket': listmeticket, 'openticket': openticket,
            'openticketyesterday': openticketyesterday, 'listopenticketcloseticket': listopenticket,
            'closeticket': closeticket, 'listcloseticket': listcloseticket, 'count_unit': count_unit,
            'napaydari_list': napydarilist,
            'rpm': rpm, 'napaydari': napaydari, 'date_nosell': date_nosell, 'nosell': nosell, 'gscount': gscount,
            'nazelcount': nazelcount, 'stars': stars, 'napaydari_today': napaydari_today

            }
