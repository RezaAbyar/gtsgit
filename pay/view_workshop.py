import math
from datetime import datetime, date
import datetime
from operator import itemgetter
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side, BORDER_THIN
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, When, Case
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from django.contrib import messages
from rest_framework.permissions import IsAuthenticated
from base.filter import StoreFilters
from base.forms import open_excel
from util import DENY_PAGE, HOME_PAGE, SUCCESS_MSG, EXCEL_MODE, DATE_FORMAT, PAY_PAGE, SENDLIST_PAGE, ZONE_NAME, \
    ADD_STORE_MSG, EXCEL_EXPORT_FILE
from .models import PayBaseParametrs, Owner, Payroll, StoreList, Store, StoreHistory, PayItems, PayParametr, \
    PayDarsadMah, HistorySt, Post, Tektaeed, StatusRef, StatusStore, TekKarkard, BaseGroup, RepairStoreName, Tadiltemp, \
    Repair, StoreView, RepairStore, kargahToStorage
from base.models import Mount, UserPermission, DefaultPermission, Zone, Storage, UploadExcel, Pump, Ticket, \
    GsModel
from django.http import HttpResponse, JsonResponse
from jalali.Jalalian import JDate
import jdatetime
from django.db import IntegrityError
from accounts.logger import add_to_log
from django.views import View
from .forms import RepairForm

def sendlistworkshop(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='takhsisstorage')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    _list = None
    _list = Store.objects.filter(status_id__in=[1,14],storage_id=request.user.owner.storage_id, zone__storage=True).order_by('-id')

    return render(request, 'store/sendlistworkshop.html',
                  {'list': _list,
                   'formpermmision': formpermmision,})

def sendzoneworkshop(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)

    ua = owner_p.get(permission__name='takhsisstorage')
    if ua.accessrole.ename == 'no':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    storages = None
    zonelist = None


    storages = Storage.objects.filter(zone_id=request.user.owner.zone_id)
    zonelist = kargahToStorage.objects.filter(zone_id=request.user.owner.zone_id)

    if request.method == 'POST':
        master = int(request.POST.get('master'))
        zone = int(request.POST.get('zone'))
        pinpad = request.POST.get('pinpad')
        storage = int(request.POST.get('storage'))
        select = request.POST.get('select')
        _type = request.POST.get('type')
        az = select
        select = select.split("/")
        if _type == "1":
            _ty=14
            _info='ثبت تخصیص قطعه داغی برای '
        else:
            _ty=1
            _info='ثبت تخصیص قطعه سالم برای '
        select = jdatetime.date(day=int(select[2]), month=int(select[1]), year=int(select[0])).togregorian()
        mystore = Store.objects.create(owner_id=request.user.owner.id, tarikh=select, pinpad=pinpad, master=master,
                                       status_id=_ty,
                                       zone_id=zone, storage_id=storage)
        mystore.create = f'{select} 11:11:11'
        mystore.save()
        add_to_log(request, _info + str(mystore.zone.name),0)
        HistorySt.objects.create(store_id=mystore.id, owner_id=request.user.owner.id,
                                 status_id=_ty, description=f' تخصیص به   {mystore.zone.name} ')
        messages.success(request, SUCCESS_MSG)

    return render(request, 'store/sendzoneworkshop.html',
                  {'formpermmision': formpermmision, 'zone': zonelist, 'storages': storages})