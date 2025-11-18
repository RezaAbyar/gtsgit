from django.db.models import F, Avg, Count, Sum, When, Case
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from base.models import Area, GsModel, Pump, Ticket, Zone, FailureSub
from rest_framework.views import APIView
import random
from django.db import IntegrityError
from operator import itemgetter
from sell.models import SellModel
from .init import CoreAPIView, BaseAPIView
from .utils import string_assets
from .utils.exception_helper import BadRequest
from django.core.exceptions import ValidationError
import datetime
from rest_framework.permissions import IsAuthenticated
from datetime import date
from base.modelmanager import RoleeManager


def zoneorarea(request):
    _roleid = 0
    if request.user.owner.role.role in ['zone','engin']:
        _roleid = request.user.owner.zone_id
    elif request.user.owner.role.role == 'area':
        _roleid = request.user.owner.area_id
    elif request.user.owner.role.role == 'tek':
        _roleid = request.user.owner.id
    return _roleid


class GetLiveInfo(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        openticketyesterday = 0
        openticket = 0
        count_me = 0
        closeticket = 0
        count_failure = []
        _today = date.today()
        napaydari_today = 0
        napaydari = 0
        rpm = 0
        nosell = 0
        count_fani = 0
        count_test = 0
        count_engin = 0
        count_tek = 0
        this_date = datetime.datetime.today()

        count_fani = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                    organization_id=2,

                                                                    ).count()
        count_test = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                    organization_id=3,

                                                                    ).count()
        count_engin = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                     organization_id=4,

                                                                     ).count()
        count_tek = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                   organization_id=1,

                                                                   ).count()
        openticket = Ticket.object_role.c_gs(request,0).annotate(count=Count('id')).filter(
            status__status='open').exclude(organization_id=4).count()
        count_me = Ticket.object_role.c_gs(request,0).filter(organization_id=5,
                                                                  status_id=1).count()
        closeticket = Ticket.object_role.c_gs(request,0).filter(closedate__year=_today.year,
                                                                     closedate__month=_today.month,
                                                                     closedate__day=_today.day,
                                                                     status__status='close').count()
        openticketyesterday = Ticket.object_role.c_gs(request,0).exclude(organization_id=4).filter(
            status__status='open', create__date__year=_today.year, create__date__month=_today.month,
            create__date__day=_today.day).count()
        napaydari = Ticket.object_role.c_gs(request,0).values('gs_id').filter(
            status__status='open', gs__active=True,
            failure_id=1056, status_id=1, is_system=True).count()
        rpm = Ticket.object_role.c_gs(request,0).values('gs_id').filter(
            status__status='open', gs__active=True,
            failure_id=1164, status_id=1, is_system=True).count()

        napaydari_today = Ticket.object_role.c_gs(request,0).values('gs_id').filter(
            gs__active=True, create__date__year=_today.year, create__date__month=_today.month,
            create__date__day=_today.day,
            failure_id=1056, status_id=1, is_system=True).count()
        gsmodel = GsModel.object_role.c_gsmodel(request).filter(active=True)
        nosell = gsmodel.exclude(
            id__in=SellModel.object_role.c_gs(request,0).filter(sell__gte=5, sellkol__gte=500,
                                                                     tarikh=this_date - datetime.timedelta(
                                                                         days=1)).values('gs_id')).count()
        if request.user.owner.role.role in ['fani', 'test']:

            count_failures = Ticket.object_role.c_gs(request,0).values('failure_id', 'failure__info').filter(
                status__status='open', organization_id__in=[2, 3]).annotate(tedad=Count('id')).order_by('-tedad')
            for item in count_failures:
                dict={
                    'name':item['failure__info'][:30],
                    'tedad':item['tedad']
                }

                count_failure.append(dict)




        return JsonResponse(
            {'openticket': openticket, 'closeticket': closeticket, 'count_me': count_me,
             'openticketyesterday': openticketyesterday, 'napaydari': napaydari, 'count_failure': count_failure,
             'rpm': rpm, 'napaydari_today': napaydari_today, 'nosell': nosell,
             'count_fani': count_fani, 'count_test': count_test, 'count_tek': count_tek, 'count_engin': count_engin,
             'message': 'success'})


class GetLiveBohran(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        mlist = []
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        err_init = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                  organization_id=1, failure_id__in=[1172]
                                                                  ).count()
        no_init = Ticket.object_role.c_gs(request,0).filter(status__status='open',
                                                                 organization_id=2, failure_id__in=[1172]
                                                                 ).count()
        ok_init = Ticket.object_role.c_gs(request,0).values('gs').filter(status__status='close',
                                                                              organization_id=2,
                                                                              failure_id__in=[1171, 1172]
                                                                              ).annotate(tedad=Count('gs'))
        ok_init = ok_init.count()
        # ok_init = ok_init['tedad']
        # ok_init = ok_init.filter(status__status='close',
        #                                                          organization_id=2, failure_id__in=[1171, 1172]
        #                                                          ).count()
        _sum = no_init + ok_init + err_init

        _list = Ticket.object_role.c_gs(request,0).values('gs__area__zone__name', 'gs__area__zone_id').filter(
            failure_id__in=[1172]).annotate(
            ok_init=Count(Case(When(status_id=2, then=1))),
            no_init=Count(Case(When(status_id=1, organization_id=2, then=1))),
            err_init=Count(Case(When(status_id=1, organization_id=1, then=1))))

        for item in _list:
            dict = {
                'zone': item['gs__area__zone__name'],
                'zoneid': item['gs__area__zone_id'],
                'ok_int': item['ok_init'],
                'no_int': item['no_init'],
                'err_int': item['err_init'],
            }

            mlist.append(dict)
            mlist = sorted(mlist, key=itemgetter('ok_int'), reverse=True)

        return JsonResponse(
            {'no_init': no_init, 'ok_init': ok_init, 'sums': _sum, 'err_init': err_init,
             'mlist': mlist})
