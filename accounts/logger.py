from lock.models import LockLogs
from .models import Logs
import uuid
import socket


def add_to_log(request, parametr1, gs):
    try:
        hostname = socket.gethostname()
    except:
        hostname = "0"

    user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip:
        ip = user_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if request.user.is_authenticated:
        Logs.objects.create(owner_id=request.user.owner.id, parametr1=parametr1, parametr2=ip, gs=gs,
                            macaddress=str(hostname))
    else:
        Logs.objects.create(parametr1=parametr1, parametr2=ip, macaddress=str(hostname))


# def add_log_lock(request, status, lockmodel, position, gs, pump):
#     LockLogs.objects.create(owner_id=request.user.owner.id, lockmodel_id=lockmodel, position_id=position,
#                             gs_id=gs, pump_id=pump, status_id=status
#                             )
