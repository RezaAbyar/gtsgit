from .models import Ticket, GsModel
import random

"""
step1 Run Query
# UPDATE sell_sellmodel set start=0 WHERE start is NULL;
# UPDATE sell_sellmodel set end=0 WHERE end is NULL;
"""
def addrndticket():
    for ticket in Ticket.objects.all():
        code = random.randint(1000000, 9999999)
        ticket.rnd = code
        ticket.save()
    return True

def addrndgs():
    for gs in GsModel.objects.all():
        code = random.randint(1000000, 9999999)
        gs.rnd = code
        gs.save()
    return True
