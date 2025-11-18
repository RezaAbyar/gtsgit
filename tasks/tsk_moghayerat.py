import os
import django
from django.conf import settings
from datetime import datetime
from django.db.models import Sum
from jalali.Jalalian import JDate
import datetime
import redis
from base.models import Pump
from sell.models import SellModel


def moghayerat():
    rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                     password=settings.REDIS_PASS)
    if rd.exists('moghayerat'):
        print('Delete Old Data')
        rd.delete('moghayerat')
    print('Start Configuration')
    mount_ago = datetime.date.today() - datetime.timedelta(days=370)
    today_ago = datetime.date.today() - datetime.timedelta(days=2)

    sell = SellModel.objects.values('gs__area__zone_id', 'gs__area__zone__name').filter(
        tarikh__range=(mount_ago, today_ago), ).annotate(jam=Sum('nomojaz'))

    jd = JDate(mount_ago.strftime("%Y-%m-%d %H:%M:%S"))
    azdate = jd.format('Y/m/d')
    jd = JDate(today_ago.strftime("%Y-%m-%d %H:%M:%S"))
    tadate = jd.format('Y/m/d')
    info = f'(از تاریخ {azdate}  تا {tadate})'
    print('End Configuration')
    print('Start Task...')
    for item in sell:
        storecount = Pump.objects.filter(gs__area__zone_id=item['gs__area__zone_id'],
                                         status__status=True).count()
        name = str(item['gs__area__zone__name'])
        _result = str(name) + "%" + str(round(int(item['jam']))) + "%" + str(
            round((int(item['jam']) / storecount) * 100, 2), ) + "%" + str(info)
        rd.hsetnx('moghayerat', str(item['gs__area__zone_id']), _result)
        rd.expire('moghayerat', 3600)


    print('End Task...')


