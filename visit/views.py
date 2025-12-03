import datetime
import jdatetime
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator

from accounts.logger import add_to_log
from base.filter import StoreFilters
from base.permission_decoder import cache_permission
from base.views import zoneorarea
from django.db import IntegrityError
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from util import DENY_PAGE, HOME_PAGE
from utils.exception_helper import to_miladi
from base.models import UserPermission, DefaultPermission, Pump
from base.views import checkxss
from sell.models import Mojodi, SellGs, SellModel
from .models import *
from django.db.models import Count, Sum, Q, Avg, Case, When, Value, IntegerField
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import CertificateType, Certificate, CertificateAlert
from .forms import CertificateTypeForm, CertificateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


today = str(jdatetime.date.today())

today = today.replace("-", "/")
from .forms import EmergencyFuelingForm, EmergencyPermissionForm
from jdatetime import date as jdate


@cache_permission('emergency')
def emergency_fueling_create(request):
    _permission = EmergencyPermission.objects.filter(
        station_name__gsowner__owner=request.user.owner,
        used=False
    )

    if request.method == 'POST':
        form = EmergencyFuelingForm(request.POST, request=request)
        # return HttpResponse(form)
        if not form.is_valid():
            return HttpResponse(form)
        if form.is_valid():
            fueling = form.save(commit=False)
            fueling.fueling_date = timezone.now().date()
            fueling.created_by = request.user.owner

            # تعیین جایگاه از روی کاربر
            if hasattr(request.user, 'owner') and request.user.owner.gslist_set.exists():
                fueling.station_name = request.user.owner.gslist_set.first().gs
                fueling.owner = request.user.owner

            # اگر گزینه "فاقد مجوز" انتخاب شده
            # fueling.owner.id = request.user.owner.id
            # fueling.station_name.id = request.user.owner.gslist_set.first().gs
            if request.POST.get('station_name') == '0':
                # استفاده از اطلاعات وارد شده توسط کاربر
                fueling.plate_number = form.cleaned_data['plate_number']
                fueling.liters = form.cleaned_data['liters']
                fueling.permission = None  # بدون مجوز
            else:
                # استفاده از اطلاعات مجوز انتخاب شده
                permission_id = request.POST.get('station_name')
                try:
                    permission = EmergencyPermission.objects.get(id=permission_id)
                    fueling.plate_number = permission.plate_number
                    fueling.liters = permission.liters
                    fueling.permission = permission
                except EmergencyPermission.DoesNotExist:
                    messages.error(request, 'مجوز انتخاب شده یافت نشد.')
                    return render(request, 'emergency_fueling_form.html', {'form': form, 'permission': _permission})

            try:
                fueling.save()
                messages.success(request, 'سوخت‌گیری با موفقیت ثبت شد.')
                return redirect('visit:emergency_fueling_list')
            except Exception as e:
                messages.error(request, f'خطا در ثبت: {str(e)}')
                return redirect('visit:emergency_fueling_create_form')
    else:
        form = EmergencyFuelingForm(request=request)

    return TemplateResponse(request, 'emergency_fueling_form.html', {'form': form, 'permission': _permission})

@cache_permission('emergency')
def emergency_permission_create(request):
    if request.method == 'POST':
        gregorian_date = None
        form = EmergencyPermissionForm(request.POST, request=request)
        _expired_date = request.POST.get('expired_date')
        if _expired_date:
            year, month, day = map(int, _expired_date.split('/'))
            gregorian_date = jdatetime.date(year, month, day).togregorian()

        if form.is_valid():
            permission = form.save(commit=False)
            permission.owner = request.user.owner
            permission.expired_date = gregorian_date

            try:
                permission.save()
                messages.success(request, 'مجوز با موفقیت ایجاد شد.')
                return redirect('emergency_permission_list')
            except Exception as e:
                messages.error(request, f'خطا در ثبت: {str(e)}')

        else:
            messages.error(request, f'خطا در ثبت: {str(form.errors)}')
    else:
        form = EmergencyPermissionForm(request=request)

    return TemplateResponse(request, 'emergency_permission_form.html', {'form': form})


def check_duplicate_fueling(request):
    plate_number = request.GET.get('plate_number', '')
    today = timezone.now().date()

    exists = EmergencyFueling.objects.filter(
        plate_number=plate_number,
        fueling_date=today
    ).exists()

    return JsonResponse({'exists': exists})


@cache_permission('emergency')
def emergency_fueling_list(request):
    fuelings = EmergencyFueling.objects.all().order_by('-created_at')
    return TemplateResponse(request, 'emergency_fueling_list.html', {'fuelings': fuelings})


@cache_permission('emergency')
def emergency_permission_list(request):
    permissions = EmergencyPermission.objects.all().order_by('-created_at')
    return TemplateResponse(request, 'emergency_permission_list.html', {'permissions': permissions})


from django.db import DatabaseError
from django.core.exceptions import ValidationError


@cache_permission('sarakkasri')
def sarakkasriview(request, _id, _st):
    try:
        _reside = None
        _gs = 1
        _product = 2
        _reside = None
        _mojodi = None
        _date = None
        _tarikh = None
        _sell = None
        _lastdore = ""
        _list = []

        if _id == 0:
            sarak = None
            pumps = None
        else:
            try:
                sarak = SarakKasri2.objects.get(id=_id)
                _date = sarak.tarikh_start
                _gs = sarak.gs_id
                _product = sarak.product.id
                pumps = Pump.objects.filter(gs_id=_gs, product_id=_product)
                _tarikh = sarak.tarikh
                _lastdore = sarak.lastdore
                _stkasri = 0 if int(sarak.saraknamojaz) >= 0 else 1
                dict = {
                    'product': sarak.product.name,
                    "start_mojodi": sarak.mojodi_startdore + sarak.azmayesh,
                    'sell': sarak.sell,
                    'sell2': sarak.sell2,
                    'stkasri': _stkasri,
                    'mojodiandreside': (sarak.mojodi_startdore + sarak.azmayesh) + sarak.barname,
                    'kasrmojodiandforosh': (sarak.mojodi_startdore + sarak.azmayesh + sarak.barname) - (sarak.sell),
                    'kasristart': sarak.sarakazebteda,
                    'kasrimojaz': sarak.kasrimojazi,
                    'kasrinamojaz': sarak.saraknamojaz,
                    'mojodi': sarak.mojodi_in_check,
                    'moghayeratdip': round((sarak.mojodi_enddore - sarak.sell2) - sarak.mojodi_in_check)
                }
                _list.append(dict)
            except SarakKasri2.DoesNotExist:
                messages.error(request, 'رکورد سرک و کسری مورد نظر یافت نشد.')
                return redirect('visit:sarakkasrilist')
            except Exception as e:
                messages.error(request, f'خطا در بارگذاری داده‌ها: {str(e)}')
                return redirect('visit:sarakkasrilist')

        start_mojodi = 0
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        gslist = GsModel.object_role.c_gsmodel(request).filter(status__status=True)
        today = datetime.date.today() - datetime.timedelta(days=1)
        if request.method == 'POST':
            try:
                _list = []
                _gs = request.POST.get('gs')
                _product = request.POST.get('product')
                _tarikh = request.POST.get('tarikh')

                # اعتبارسنجی داده‌های ورودی
                if not all([_gs, _product, _tarikh]):
                    messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید.')
                    return redirect('visit:sarakkasrilist', _id=_id, _st=_st)

                _date = to_miladi(_tarikh)
                _mojodi = request.POST.get('mojodi', 0)
                _azmayesh = request.POST.get('azmayesh', 0)
                _start_mojodiold = request.POST.get('mojodi_start', 0)
                _last_mojodi = request.POST.get('mojodi_end', 0)
                _reside = request.POST.get('reside', 0)
                _sell = int(request.POST.get('sell', 0))
                _sell2 = int(request.POST.get('sell2', 0))
                _start_mojodi = int(_azmayesh) + int(_start_mojodiold)

                # اعتبارسنجی مقادیر عددی
                # try:
                #     _mojodi = float(_mojodi)
                #     _azmayesh = float(_azmayesh)
                #     _start_mojodiold = float(_start_mojodiold)
                #     _last_mojodi = float(_last_mojodi)
                #     _reside = float(_reside)
                # except ValueError:
                #     messages.error(request, 'مقادیر عددی وارد شده نامعتبر هستند.')
                #     return redirect('sarakkasri_view', _id=_id, _st=_st)

                lastdore = SellGs.objects.filter(gs_id=_gs, product_id=_product).order_by('-tarikh').first()
                if lastdore:
                    _lastdore = str(lastdore.tarikh)
                    _lastdore = _lastdore.replace("-", "/")

                if _product == "2":
                    product = 'بنزین معمولی'
                    darsad = 0.0045
                elif _product == "3":
                    product = 'بنزین سوپر'
                    darsad = 0.0045
                elif _product == "4":
                    product = 'نفتگاز'
                    darsad = 0
                else:
                    messages.error(request, 'نوع فرآورده انتخاب شده نامعتبر است.')
                    return redirect('visit:sarakkasrilist', _id=_id, _st=_st)

                _kasristart = round(
                    ((int(_start_mojodi) + int(_reside)) - (float(_sell) + float(_sell2))) - int(_mojodi))
                _kasrimojaz = round((int(_start_mojodi) + int(_reside)) * darsad)
                _kasrinamojaz = _kasrimojaz - _kasristart

                if _kasrimojaz >= _kasristart:
                    _kasrinamojaz = 0

                _stkasri = 0 if _kasrinamojaz >= 0 else 1

                dict = {
                    'product': product,
                    "start_mojodi": _start_mojodi,
                    'sell': round(float(_sell)),
                    'sell2': float(_sell2),
                    'mojodiandreside': round(int(_start_mojodi) + int(_reside)),
                    'kasrmojodiandforosh': round((int(_start_mojodi) + int(_reside)) - (float(_sell) + float(_sell2))),
                    'kasristart': _kasristart,
                    'kasrimojaz': _kasrimojaz,
                    'kasrinamojaz': _kasrinamojaz,
                    'stkasri': _stkasri,
                    'mojodi': _mojodi,
                    'moghayeratdip': round((float(_last_mojodi) - float(_sell2)) - int(_mojodi))
                }
                _list.append(dict)

                try:
                    # ایجاد یا به‌روزرسانی رکورد
                    sarak, created = SarakKasri2.objects.update_or_create(
                        gs_id=int(_gs),
                        product_id=int(_product),
                        tarikh_start=_date,
                        defaults={
                            'mojodi_in_check': _mojodi,
                            'tarikh': _tarikh,
                            'tarikhakharindore': _lastdore,
                            'kasrimojazi': _kasrimojaz,
                            'barname': _reside,
                            'azmayesh': _azmayesh,
                            'mojodi_startdore': _start_mojodiold,
                            'mojodi_enddore': _last_mojodi,
                            'sarakazebteda': _kasristart,
                            'saraknamojaz': _kasrinamojaz,
                            'sarakmoghayerat': round((float(_last_mojodi) - float(_sell2)) - int(_mojodi)),
                            'owner_id': request.user.owner.id,
                            'sell': _sell,
                            'sell2': _sell2,
                            'lastdore': _lastdore,
                            'uniq': f"{_gs}-{_product}-{_date}"
                        }
                    )

                    if created:
                        messages.success(request, 'اطلاعات سرک و کسری با موفقیت ذخیره شد.')
                    else:
                        messages.success(request, 'اطلاعات سرک و کسری با موفقیت به‌روزرسانی شد.')

                except IntegrityError as e:
                    messages.error(request, 'خطای یکتایی: این رکورد قبلاً ذخیره شده است.')
                    return redirect('visit:sarakkasrilist', _id=_id, _st=_st)
                except DatabaseError as e:
                    messages.error(request, 'خطای پایگاه داده در ذخیره اطلاعات. میزان فروش دوره نباید منفی باشد ')
                    return redirect('visit:sarakkasrilist', _id=_id, _st=_st)
                except Exception as e:
                    messages.error(request, f'خطای غیرمنتظره در ذخیره اطلاعات: {str(e)}')
                    return redirect('visit:sarakkasrilist', _id=_id, _st=_st)

            except Exception as e:
                messages.error(request, f'خطا در پردازش اطلاعات: {str(e)}')
                return redirect('visit:sarakkasrilist', _id=_id, _st=_st)

        # ادامه کد برای نمایش اطلاعات
        try:
            nsells = Sells.objects.filter(gs_id=_gs, pump__product_id=_product, tarikh=_date)
            sumsell = nsells.aggregate(sell=Sum('sell'))
            sumsell2 = nsells.aggregate(sell=Sum('sell2'))
            sumsell3 = nsells.aggregate(sell=Sum('sell') + Sum('sell2'))
        except Exception as e:
            messages.warning(request, f'خطا در بارگذاری اطلاعات فروش: {str(e)}')
            nsells = []
            sumsell = {'sell': 0}
            sumsell2 = {'sell': 0}
            sumsell3 = {'sell': 0}

        content = {'gslist': gslist, 'product': int(_product), 'gs': int(_gs), 'date': _date, 'mojodi': _mojodi,
                   'tarikh': _tarikh, 'tarikh2': _lastdore, 'today': today, 'sarak': sarak, 'sumsell': sumsell,
                   'sumsell2': sumsell2, 'pumps': pumps, 'sumsell3': sumsell3,
                   'nsells': nsells,
                   'reside': _reside, 'sell': _sell, 'lists': _list}

        if _st == 1:
            template_file = 'sarakkasri.html'
        else:
            template_file = 'printsarakkasri.html'

        return TemplateResponse(request, template_file, content)

    except Exception as e:
        messages.error(request, f'خطای سیستمی: {str(e)}')
        return redirect('visit:sarakkasrilist')  # یا redirect به صفحه مناسب دیگر


def listnazel(request):
    _product = request.GET.get('product')
    gsid = request.GET.get('gsid')
    mylist = []
    pumps = Pump.objects.filter(gs_id=gsid, status__status=True, product_id=_product).order_by('number')
    for pump in pumps:
        _dict = {
            "id": pump.id,
            'name': pump.product.name,
            'number': pump.number
        }
        mylist.append(_dict)
    return JsonResponse({'mylist': mylist})


def savesellsarak(request):
    gsid = request.POST.get('gsid')
    _product = request.POST.get('product')
    val = request.POST.get('val')
    tarikh = request.POST.get('tarikh')
    start = request.POST.get('start')
    end = request.POST.get('end')
    endsell = request.POST.get('endsell')
    sell = request.POST.get('sell')
    _tarikh = to_miladi(tarikh)

    if not all([gsid, _product, val, tarikh, start, end, endsell]):
        return JsonResponse({'status': 'error', 'message': 'لطفاً تمام فیلدها را پر کنید.'})

    _sell = SellModel.objects.filter(tolombeinfo_id=val, gs_id=gsid, product_id=_product,
                                     tarikh__range=(_tarikh, datetime.date.today())).aggregate(sell=Sum('sell'))
    sell = _sell['sell']
    mylist = []
    tarikh = to_miladi(tarikh)
    _sell2 = int(start) - int(endsell)

    try:
        Sells.objects.create(gs_id=gsid, tarikh=tarikh, start=start, end=end, sell=sell, owner_id=request.user.owner.id,
                             end2=endsell, sell2=_sell2,
                             pump_id=val, uniq=str(gsid) + "-" + str(tarikh) + "-" + str(val))
    except IntegrityError:
        _sell = Sells.objects.get(gs_id=gsid, tarikh=tarikh, pump_id=val)
        _sell.start = start
        _sell.end = end
        _sell.sell = sell
        _sell.sell2 = _sell2
        _sell.end2 = endsell
        _sell.save()

    sells = Sells.objects.filter(gs_id=gsid, tarikh=tarikh, pump__product_id=_product)
    summsell = sells.aggregate(summ=Sum('sell'), summ2=Sum('sell2'))
    for sell in sells:
        _dict = {
            "id": sell.id,
            'name': sell.pump.product.name,
            'number': sell.pump.number,
            'start': sell.start,
            'end': sell.end,
            'sell': sell.sell + sell.sell2
        }
        mylist.append(_dict)
    return JsonResponse({'mylist': mylist, 'summsell': summsell['summ'], 'summsell2': summsell['summ2']})


def loadsellsarak(request):
    gsid = request.POST.get('gsid')
    tarikh = request.POST.get('tarikh')
    _product = request.POST.get('product')
    if len(tarikh) < 5:
        return JsonResponse({'meg': 'err'})
    tarikh = to_miladi(tarikh)
    tarikh = tarikh - datetime.timedelta(days=1)
    mylist = []
    sells = Sells.objects.filter(gs_id=gsid, tarikh=tarikh, pump__product_id=_product)
    summsell = sells.aggregate(summ=Sum('sell'), summ2=Sum('sell2'))
    _si = 0
    try:
        start_mojodi = Mojodi.objects.get(gs_id=gsid, tarikh=tarikh)
    except Mojodi.DoesNotExist:
        start_mojodi = None
        _si = 1
    end_mojodi = Mojodi.objects.filter(gs_id=gsid).order_by('-tarikh').first()
    if _product == "2":
        product = 'بنزین معمولی'
        _start_mojodi = start_mojodi.benzin if _si == 0 else 0
        _end_mojodi = end_mojodi.benzin

    elif _product == "3":
        product = 'بنزین سوپر'

        _start_mojodi = start_mojodi.super if _si == 0 else 0
        _end_mojodi = end_mojodi.super
        darsad = 0.0045

    elif _product == "4":
        product = 'نفتگاز'
        _start_mojodi = start_mojodi.gaz if _si == 0 else 0
        _end_mojodi = end_mojodi.gaz

        darsad = 0
    for sell in sells:
        _dict = {
            "id": sell.id,
            'name': sell.pump.product.name,
            'number': sell.pump.number,
            'start': sell.start,
            'end': sell.end,
            'sell': sell.sell
        }
        mylist.append(_dict)
    return JsonResponse(
        {'mylist': mylist, 'summsell': summsell['summ'], 'summsell2': summsell['summ2'], 'start_mojodi': _start_mojodi,
         'end_mojodi': _end_mojodi})


@cache_permission('sarakkasri')
def sarakkasrilist(request):
    _list = None
    add_to_log(request, f'مشاهده فرم  سرک و کسری ', 0)
    list2 = None
    datein = str(request.GET.get('select'))
    dateout = str(request.GET.get('select2'))

    if len(datein) < 10:
        datein = "2023-01-01"
        dateout = "9999-12-30"
    else:
        datein = datein.split("/")
        dateout = dateout.split("/")

        datein = jdatetime.date(day=int(datein[2]), month=int(datein[1]), year=int(datein[0])).togregorian()
        dateout = jdatetime.date(day=int(dateout[2]), month=int(dateout[1]), year=int(dateout[0])).togregorian()
        datein = str(datein) + " 00:00:01"
        dateout = str(dateout) + " 23:59:59"
    if request.user.owner.role.role == 'mgr':
        _list = SarakKasri2.objects.filter(tarikh_start__gte=datein, tarikh_start__lte=dateout,
                                           ).order_by('-id')
    if request.user.owner.role.role == 'setad':
        _list = SarakKasri2.objects.filter(tarikh_start__gte=datein, tarikh_start__lte=dateout,
                                           ).order_by(
            '-id')

    if request.user.owner.role.role == 'zone':
        _list = SarakKasri2.objects.filter(tarikh_start__gte=datein, tarikh_start__lte=dateout,
                                           gs__area__zone_id=request.user.owner.zone_id,
                                           ).order_by('-id')
    if request.user.owner.role.role == 'area':
        _list = SarakKasri2.objects.filter(tarikh_start__gte=datein, tarikh_start__lte=dateout,
                                           gs__area_id=request.user.owner.area_id,
                                           ).order_by('-id')

    paginator = Paginator(_list, 37)
    page_num = request.GET.get('page')

    data = request.GET.copy()
    this_date = datetime.datetime.today()

    if 'page' in data:
        del data['page']

    query_string = request.META.get("QUERY_STRING", "")
    if query_string.startswith("page"):
        query_string = query_string.split("&", 1)
        query_string = query_string[1]

    page_object = paginator.get_page(page_num)
    page_obj = paginator.num_pages
    tedad = paginator.count

    this_date = str(this_date)
    this_date = this_date.split(' ')
    this_date = this_date[0]
    today_date = str(datetime.datetime.today())
    today_date = today_date.split(' ')
    today_date = today_date[0]
    return TemplateResponse(request, 'listsarakkasri.html',
                            {'list': page_object, 'query_string': query_string, 'this_date': this_date,
                             'today_date': today_date, 'page_num': page_num,
                             'page_obj': page_obj, 'tedad': tedad})


class ZoneBasedListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'owner') and self.request.user.owner.zone:
            if hasattr(self.model, 'area__zone'):
                return qs.filter(area__zone=self.request.user.owner.zone)
            elif hasattr(self.model, 'zone'):
                return qs.filter(zone=self.request.user.owner.zone)
            elif hasattr(self.model, 'gs__area__zone'):
                return qs.filter(gs__area__zone=self.request.user.owner.zone)
        return qs


class CertificateTypeListView(LoginRequiredMixin, ListView):
    model = CertificateType
    template_name = 'madarek/certificate_type_list.html'
    context_object_name = 'certificate_types'

    @method_decorator(cache_permission('certificateadmin'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CertificateTypeCreateView(LoginRequiredMixin, CreateView):
    model = CertificateType
    form_class = CertificateTypeForm
    template_name = 'madarek/certificate_type_form.html'
    success_url = reverse_lazy('visit:certificate_type_list')

    @method_decorator(cache_permission('certificateadmin'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'نوع گواهی با موفقیت ایجاد شد.')
        return super().form_valid(form)


class CertificateTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = CertificateType
    form_class = CertificateTypeForm
    template_name = 'madarek/certificate_type_form.html'
    success_url = reverse_lazy('visit:certificate_type_list')

    @method_decorator(cache_permission('certificateadmin'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'نوع گواهی با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


# class CertificateListView(ZoneBasedListView):
#     model = Certificate
#     template_name = 'madarek/certificate_list.html'
#     context_object_name = 'certificates'
#
#     @method_decorator(cache_permission('certificate'))
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         if self.request.user.owner.role.role in ['zone', 'engin']:
#             queryset = queryset.filter(gs__area__zone_id=self.request.user.owner.zone_id)
#         if self.request.user.owner.role.role == 'area':
#             queryset = queryset.filter(gs__area_id=self.request.user.owner.area_id)
#         if self.request.user.owner.role.role in ['gs', 'tek']:
#             queryset = queryset.filter(gs__gsowner__owner_id=self.request.user.owner.id)
#         return queryset


@cache_permission('certificate')
def certificate_list_view(request):
    zones = Zone.objects_limit.all()
    certificatetypes = CertificateType.objects.all()
    gs_list = GsModel.objects.all()

    # فیلتر براساس نقش کاربر
    if request.user.owner.role.role in ['zone', 'engin']:
        gs_list = gs_list.filter(area__zone_id=request.user.owner.zone_id)
    if request.user.owner.role.role == 'area':
        gs_list = gs_list.filter(area_id=request.user.owner.area_id)
    if request.user.owner.role.role in ['gs', 'tek']:
        gs_list = gs_list.filter(gsowner__owner_id=request.user.owner.id)

    # اعمال فیلترها
    if request.method == 'POST':
        zone_id = request.POST.get('zone')
        area_id = request.POST.get('area')
        gs_id = request.POST.get('gs')
        product_id = request.POST.get('product')

        if request.user.owner.role.role in ['zone', 'engin']:
            zone_id = request.user.owner.zone_id
        if request.user.owner.role.role == 'area':
            area_id = request.user.owner.area_id

        if gs_id != '0':
            gs_list = gs_list.filter(id=gs_id)
        elif area_id != "0":
            gs_list = gs_list.filter(area_id=area_id)
        elif zone_id != "0":
            gs_list = gs_list.filter(area__zone_id=zone_id)

    context = {
        'gs_list': gs_list,  # لیست جایگاه‌ها
        'zones': zones,
        'certificatetypes': certificatetypes,
    }

    return TemplateResponse(request, 'madarek/certificate_gs_list.html', context)


@cache_permission('certificate')
def certificate_gs_detail_view(request, gs_id):
    """نمایش آخرین مدارک هر نوع برای یک جایگاه خاص"""
    gs = get_object_or_404(GsModel, id=gs_id)

    # بررسی دسترسی کاربر به این جایگاه
    if not has_access_to_gs(request.user, gs):
        return redirect('deny')

    # دریافت آخرین مدرک از هر نوع برای این جایگاه
    latest_certificates = []
    certificate_types = CertificateType.objects.all()

    for cert_type in certificate_types:
        latest_cert = Certificate.objects.filter(
            gs=gs,
            certificate_type=cert_type
        ).order_by('-issue_date').first()

        if latest_cert:
            latest_certificates.append(latest_cert)

    context = {
        'gs': gs,
        'latest_certificates': latest_certificates,
        'certificate_types': certificate_types,
    }

    return TemplateResponse(request, 'madarek/certificate_gs_detail.html', context)


@cache_permission('certificate')
def certificate_history_view(request, gs_id, certificate_type_id):
    """نمایش سابقه تمام مدارک یک نوع خاص برای یک جایگاه"""
    gs = get_object_or_404(GsModel, id=gs_id)
    cert_type = get_object_or_404(CertificateType, id=certificate_type_id)

    # بررسی دسترسی کاربر
    if not has_access_to_gs(request.user, gs):
        return redirect('deny')

    # دریافت تمام مدارک این نوع برای این جایگاه
    certificates = Certificate.objects.filter(
        gs=gs,
        certificate_type=cert_type
    ).order_by('-issue_date')

    context = {
        'gs': gs,
        'certificate_type': cert_type,
        'certificates': certificates,
    }

    return TemplateResponse(request, 'madarek/certificate_history.html', context)


def has_access_to_gs(user, gs):
    """بررسی دسترسی کاربر به جایگاه"""
    if user.owner.role.role in ['admin', 'setad']:
        return True
    elif user.owner.role.role in ['zone', 'engin']:
        return gs.area.zone_id == user.owner.zone_id
    elif user.owner.role.role == 'area':
        return gs.area_id == user.owner.area_id
    elif user.owner.role.role in ['gs', 'tek']:
        return gs.gsowner.filter(owner=user.owner).exists()
    return False


@cache_permission('certificate')
def certificate_create_view(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # تبدیل تاریخ شمسی به میلادی
            jalali_date = request.POST.get('issue_date')
            jalali_date2 = request.POST.get('expiry_date')

            # اگر تاریخ به صورت رشته دریافت می‌شود (مثلاً '1402/05/15')
            if isinstance(jalali_date, str):
                year, month, day = map(int, jalali_date.split('/'))
                gregorian_date1 = jdatetime.date(year, month, day).togregorian()
                year, month, day = map(int, jalali_date2.split('/'))
                gregorian_date2 = jdatetime.date(year, month, day).togregorian()
                certificate = form.save(commit=False)
                certificate.issue_date = gregorian_date1
                certificate.expiry_date = gregorian_date2
                certificate.save()
            else:
                # اگر تاریخ به صورت datetime یا date دریافت می‌شود
                certificate = form.save()

            return redirect('visit:certificate_list')
    else:
        form = CertificateForm(user=request.user)

    return TemplateResponse(request, 'madarek/certificate_form.html', {'form': form})


# class CertificateCreateView(LoginRequiredMixin, CreateView):
#     model = Certificate
#     form_class = CertificateForm
#     template_name = 'madarek/certificate_form.html'
#     success_url = reverse_lazy('visit:certificate_list')
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def form_valid(self, form):
#         jalali_date = request.POST.get('issue_date')
#         if isinstance(jalali_date, str):
#             year, month, day = map(int, jalali_date.split('/'))
#             gregorian_date = jdatetime.date(year, month, day).togregorian()
#             form.instance.issue_date = gregorian_date
#         form.instance.uploaded_by = self.request.user
#
#         messages.success(self.request, 'گواهی با موفقیت ثبت شد.')
#         return super().form_valid(form)


class CertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = 'madarek/certificate_detail.html'
    context_object_name = 'certificate'


def check_certificate_alerts():
    now = timezone.now()
    alerts = CertificateAlert.objects.filter(
        alert_date__lte=now,
        is_sent=False
    )

    for alert in alerts:
        try:
            pass
            # ارسال ایمیل
            # send_mail(
            #     subject=f"هشدار انقضای گواهی برای جایگاه {alert.certificate.gs.name}",
            #     message=alert.message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[alert.certificate.uploaded_by.email],
            #     fail_silently=False,
            # )

            # ارسال پیام به پنل کاربری
            # (بستگی به سیستم پیام‌رسانی شما دارد)

            alert.is_sent = True
            alert.save()
        except Exception as e:
            print(f"Error sending alert: {e}")
