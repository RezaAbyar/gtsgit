import sys
import logging
from operator import itemgetter

from django.contrib.auth import login
from django.db.models import F, Avg, Count, Sum, Case, When, Max
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from jalali.Jalalian import JDate
from rest_framework import viewsets, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from cart.models import PanModels
from base.models import Area, GsModel, Pump, Ticket, Zone, FailureSub, Owner, Operator, Modem, Rack, Ipc, Status, \
    Statuspump, PumpBrand, Product, GsList, CloseGS, Baje
from rest_framework.permissions import IsAuthenticated
import jdatetime
from rest_framework.views import APIView
import random
from django.db import IntegrityError
from .init import CoreAPIView, BaseAPIView
from .utils import string_assets
from .utils.exception_helper import BadRequest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import datetime
from django.db.models import Q
from cart.views import checknumber
# import jwt



class LoginView(APIView):

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username=username).first()
        if user is None:

            raise AuthenticationFailed("Incorrect login information")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect login information")
        request.session.set_expiry(0)
        now = datetime.datetime.now()
        payload = {
            'id': user.id,
            'exp': now + datetime.timedelta(minutes=1),
            'iat': 1,
        }
        # token = jwt.encode(payload, "jkhjghftetyuuytggmjj", algorithm="HS256")
        response = Response()
        # response.set_cookie(key="jwt", value=token, httponly=False)
        # response.data = {"token": token}
        login(request, user)

        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie(key="jwt")
        response.data={'message':'logged out'}
        return response


class CardSearch(CoreAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        _listnew = []
        cd = request.GET.get('card')
        panmodel = PanModels.objects.filter(statuspan_id__in=[1, 2])
        carts = panmodel.filter(Q(pan__exact=cd) | Q(vin__exact=cd)).last()
        if carts:
            _status = 1
        else:
            carts = Baje.objects.filter(Q(pan__exact=cd) | Q(vin__exact=cd)).last()
            _status = 2 if carts else 0
        if _status == 1 or _status == 2:
            dict = {
                'status': _status,
                'gsid': carts.gs.gsid,
                'name': carts.gs.name,
                'zone': carts.gs.area.zone.name,
                'area': carts.gs.area.name,
                'location': carts.gs.location,
                'gs_address': carts.gs.address,
                'area_address': carts.gs.area.address,
                'area_lat': carts.gs.area.lat,
                'area_long': carts.gs.area.long,
                'statuspan': carts.statuspan_id,

            }
        else:
            dict={
                'status': _status
            }

        _listnew.append(dict)
        return Response(_listnew)


