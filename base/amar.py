from django.conf import settings
from django.db.models import F, Avg, Count, Sum, Case, When, Max
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from permission import GSCreatePermission
from rest_framework.views import APIView
from api.init import CoreAPIView, BaseAPIView
from api.utils import string_assets
from api.utils.exception_helper import BadRequest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import datetime
from django.db.models import Q
from .modelmanager import *
from .models import Ticket, GsModel
from .views import zoneorarea


class DarsadGsToAll(APIView):

    def get(self, request):
        # _role = request.user.owner.role.role
        # _roleid = zoneorarea(request)
        data = request.GET.get('gsid')
        _gsid = GsModel.objects.get(id=int(data))
        _list = Ticket.objects.all().aggregate(mastergs=Count(Case(When(failure_id=1045, gs_id=_gsid.id, then=1))),
                                               pinpadgs=Count(Case(When(reply_id__in=[3, 4], gs_id=_gsid.id, then=1))),
                                               masterkol=Count(Case(
                                                   When(failure_id=1045, gs__area__zone_id=_gsid.area.zone_id,
                                                        then=1))),
                                               pinpadkol=Count(Case(
                                                   When(reply_id__in=[3, 4], gs__area__zone_id=_gsid.area.zone_id,
                                                        then=1)))
                                               )
        return JsonResponse({'list': _list})
