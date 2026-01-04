from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q, F, FloatField
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
import json
from datetime import timedelta
from base.models import Area

from base.permission_decoder import cache_permission
from utils.exception_helper import to_miladi
from .models import (
    UserDistributionProfile, SuperFuelImport, ImportToDistributor,
    DistributorGasStation, DistributionToGasStation, FuelStock,
    FuelDistributionReport, SuperModel, NozzleSale, SupplierTankInventory, DailyProductPrice, Nazel,
    SupplierDailySummary
)
from base.models import Owner, Company, Product
from .forms import (
    UserDistributionProfileForm, SuperFuelImportForm, ImportToDistributorForm,
    DistributorGasStationForm, DistributionToGasStationForm,
    FuelDistributionReportForm, FuelStockUpdateForm
)
from .utils import (
    generate_import_report, generate_distribution_report,
    generate_stock_report, check_user_distribution_role
)


# ============================
# Decorators برای بررسی نقش کاربر
# ============================

def importer_required(view_func):
    """دکوراتور برای بررسی اینکه کاربر واردکننده است"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            profile = request.user.owner.distribution_profile
            if profile.role != 'importer':
                messages.error(request, 'شما دسترسی به این بخش را ندارید.')
                return redirect('fuel_distribution:dashboard')
        except UserDistributionProfile.DoesNotExist:
            messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
            return redirect('fuel_distribution:profile_create')

        return view_func(request, *args, **kwargs)

    return wrapper


def distributor_required(view_func):
    """دکوراتور برای بررسی اینکه کاربر توزیع‌کننده است"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            profile = request.user.owner.distribution_profile
            if profile.role != 'distributor':
                messages.error(request, 'شما دسترسی به این بخش را ندارید.')
                return redirect('fuel_distribution:dashboard')
        except UserDistributionProfile.DoesNotExist:
            messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
            return redirect('fuel_distribution:profile_create')

        return view_func(request, *args, **kwargs)

    return wrapper


def gas_station_required(view_func):
    """دکوراتور برای بررسی اینکه کاربر جایگاه است"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            profile = request.user.owner.distribution_profile
            if profile.role != 'gas_station':
                messages.error(request, 'شما دسترسی به این بخش را ندارید.')
                return redirect('fuel_distribution:dashboard')

            # بررسی وجود جایگاه فعال
            if not profile.active_station:
                if profile.managed_stations.exists():
                    # اگر جایگاه‌ای دارد اما فعال نیست، اولین جایگاه را فعال کن
                    profile.active_station = profile.managed_stations.first()
                    profile.save()
                    messages.info(request, f'جایگاه "{profile.active_station.name}" به عنوان جایگاه فعال تنظیم شد.')
                else:
                    messages.error(request, 'شما هیچ جایگاهی برای مدیریت ندارید. لطفاً با مدیر سیستم تماس بگیرید.')
                    return redirect('fuel_distribution:user_profile')

            # تنظیم session برای جایگاه فعال
            request.session['current_station_id'] = profile.active_station.id
            request.session['current_station_name'] = profile.active_station.name

        except UserDistributionProfile.DoesNotExist:
            messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
            return redirect('fuel_distribution:profile_create')

        return view_func(request, *args, **kwargs)

    return wrapper


@cache_permission('fuel_distribution')
def dashboard(request):
    """داشبورد اصلی بر اساس نقش کاربر"""
    try:
        profile = request.user.owner.distribution_profile
        context = {'user_profile': profile}

        if profile.role == 'importer':
            # اطلاعات واردکننده
            imports = SuperFuelImport.objects.filter(
                importer=request.user.owner
            ).order_by('-import_date')[:5]

            total_imports = SuperFuelImport.objects.filter(
                importer=request.user.owner,
                status__in=['confirmed', 'distributed']
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            pending_imports = SuperFuelImport.objects.filter(
                importer=request.user.owner,
                status='pending'
            ).count()

            distributions = ImportToDistributor.objects.filter(
                fuel_import__importer=request.user.owner
            ).order_by('-distribution_date')[:5]

            context.update({
                'imports': imports,
                'total_imports': total_imports,
                'pending_imports': pending_imports,
                'distributions': distributions,
                'role': 'importer'
            })

        elif profile.role == 'distributor':
            # اطلاعات توزیع‌کننده
            received_fuel = ImportToDistributor.objects.filter(
                distributor=request.user.owner
            ).order_by('-distribution_date')[:5]

            total_received = ImportToDistributor.objects.filter(
                distributor=request.user.owner
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            stations = DistributorGasStation.objects.filter(
                distributor=request.user.owner,
                is_active=True
            )[:5]

            deliveries = DistributionToGasStation.objects.filter(
                distributor_gas_station__distributor=request.user.owner
            ).order_by('-delivery_date')[:5]

            context.update({
                'received_fuel': received_fuel,
                'total_received': total_received,
                'stations': stations,
                'deliveries': deliveries,
                'role': 'distributor'
            })

        elif profile.role == 'gas_station':
            # اطلاعات جایگاه
            deliveries = DistributionToGasStation.objects.filter(
                distributor_gas_station__gas_station__owner=request.user.owner
            ).order_by('-delivery_date')[:5]

            total_delivered = DistributionToGasStation.objects.filter(
                distributor_gas_station__gas_station__owner=request.user.owner,
                status='delivered'
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            pending_deliveries = DistributionToGasStation.objects.filter(
                distributor_gas_station__gas_station__owner=request.user.owner,
                status='scheduled'
            ).count()

            context.update({
                'deliveries': deliveries,
                'total_delivered': total_delivered,
                'pending_deliveries': pending_deliveries,
                'role': 'gas_station'
            })

        return TemplateResponse(request, 'fuel_distribution/dashboard.html', context)

    except UserDistributionProfile.DoesNotExist:
        messages.info(request, 'لطفا پروفایل توزیع خود را تکمیل کنید.')
        return redirect('fuel_distribution:profile_create')


@cache_permission('fuel_distribution')
def user_profile(request):
    """پروفایل کاربر توزیع"""
    try:
        profile = request.user.owner.distribution_profile
    except UserDistributionProfile.DoesNotExist:
        return redirect('fuel_distribution:profile_create')

    if request.method == 'POST':
        form = UserDistributionProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد.')
            return redirect('fuel_distribution:user_profile')
    else:
        form = UserDistributionProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile
    }
    return TemplateResponse(request, 'fuel_distribution/profile/user_profile.html', context)


@cache_permission('fuel_distribution')
def create_profile(request):
    """ایجاد پروفایل توزیع"""
    if hasattr(request.user.owner, 'distribution_profile'):
        messages.info(request, 'شما قبلاً پروفایل دارید.')
        return redirect('fuel_distribution:dashboard')

    if request.method == 'POST':
        form = UserDistributionProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.owner = request.user.owner
            profile.save()
            messages.success(request, 'پروفایل با موفقیت ایجاد شد.')
            return redirect('fuel_distribution:dashboard')
    else:
        form = UserDistributionProfileForm()

    context = {'form': form}
    return TemplateResponse(request, 'fuel_distribution/profile/create_profile.html', context)


# ============================
# View های واردکننده
# ============================

@cache_permission('fuel_distribution')
@importer_required
def import_list(request):
    """لیست واردات بنزین سوپر"""
    imports = SuperFuelImport.objects.filter(
        importer=request.user.owner
    ).order_by('-import_date')

    # فیلترها
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        imports = imports.filter(status=status_filter)
    if date_from:
        imports = imports.filter(import_date__gte=date_from)
    if date_to:
        imports = imports.filter(import_date__lte=date_to)

    # صفحه‌بندی
    paginator = Paginator(imports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'imports': page_obj,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': imports.count()
    }
    return TemplateResponse(request, 'fuel_distribution/imports/list.html', context)


@cache_permission('fuel_distribution')
@importer_required
def import_create(request):
    """ثبت واردات جدید"""
    if request.method == 'POST':
        _date = request.POST.get('import_date')
        _date = to_miladi(_date)
        form = SuperFuelImportForm(request.POST, user=request.user.owner)
        if form.is_valid():
            import_record = form.save(commit=False)
            import_record.import_date = _date
            import_record.importer = request.user.owner
            import_record.company = request.user.owner.distribution_profile.company
            import_record.created_by = request.user.owner
            import_record.save()

            messages.success(request, 'ورود بنزین با موفقیت ثبت شد.')
            return redirect('fuel_distribution:import_detail', pk=import_record.pk)
    else:
        form = SuperFuelImportForm(user=request.user.owner)

    context = {
        'form': form,
        'title': 'ثبت ورود بنزین سوپر جدید'
    }
    return TemplateResponse(request, 'fuel_distribution/imports/create.html', context)


@cache_permission('fuel_distribution')
@importer_required
def import_detail(request, pk):
    """جزئیات یک ورود"""
    import_record = get_object_or_404(
        SuperFuelImport,
        pk=pk,
        importer=request.user.owner
    )

    # توزیع‌های انجام شده از این ورودی
    distributions = import_record.distributions.all()

    context = {
        'import_record': import_record,
        'distributions': distributions,
        'remaining_amount': import_record.remaining_amount
    }
    return TemplateResponse(request, 'fuel_distribution/imports/detail.html', context)


@cache_permission('fuel_distribution')
@importer_required
def import_update(request, pk):
    """ویرایش ورود"""
    import_record = get_object_or_404(
        SuperFuelImport,
        pk=pk,
        importer=request.user.owner,
        status='pending'  # فقط ورودهای در انتظار قابل ویرایش هستند
    )

    if request.method == 'POST':
        form = SuperFuelImportForm(request.POST, instance=import_record, user=request.user.owner)
        if form.is_valid():
            form.save()
            messages.success(request, 'ورود بنزین با موفقیت ویرایش شد.')
            return redirect('fuel_distribution:import_detail', pk=pk)
    else:
        form = SuperFuelImportForm(instance=import_record, user=request.user.owner)

    context = {
        'form': form,
        'title': 'ویرایش ورود بنزین',
        'import_record': import_record
    }
    return TemplateResponse(request, 'fuel_distribution/imports/create.html', context)


@importer_required
@require_POST
def import_delete(request, pk):
    """حذف ورود (فقط در صورتی که وضعیت pending باشد)"""
    import_record = get_object_or_404(
        SuperFuelImport,
        pk=pk,
        importer=request.user.owner,
        status='pending'
    )

    import_record.delete()
    messages.success(request, 'ورود بنزین با موفقیت حذف شد.')
    return redirect('fuel_distribution:import_list')


@login_required
@importer_required
@require_POST
def import_confirm(request, pk):
    """تأیید ورود بنزین"""
    import_record = get_object_or_404(
        SuperFuelImport,
        pk=pk,
        importer=request.user.owner,
        status='pending'
    )

    import_record.status = 'confirmed'
    import_record.save()

    messages.success(request, 'ورود بنزین با موفقیت تأیید شد.')
    return redirect('fuel_distribution:import_detail', pk=pk)


# ============================
# View های توزیع از واردکننده به توزیع‌کننده
# ============================

@cache_permission('fuel_distribution')
@importer_required
def distribution_list(request):
    """لیست توزیع‌های انجام شده"""
    distributions = ImportToDistributor.objects.filter(
        fuel_import__importer=request.user.owner
    ).order_by('-distribution_date')

    # فیلترها
    distributor_filter = request.GET.get('distributor', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if distributor_filter:
        distributions = distributions.filter(distributor_id=distributor_filter)
    if date_from:
        distributions = distributions.filter(distribution_date__gte=date_from)
    if date_to:
        distributions = distributions.filter(distribution_date__lte=date_to)

    # صفحه‌بندی
    paginator = Paginator(distributions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # لیست توزیع‌کننده‌ها برای فیلتر
    distributors = Owner.objects.filter(
        distribution_profile__role='distributor'
    ).values('id', 'name', 'lname')

    context = {
        'distributions': page_obj,
        'distributors': distributors,
        'distributor_filter': distributor_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': distributions.count()
    }
    return TemplateResponse(request, 'fuel_distribution/distributions/list.html', context)


@cache_permission('fuel_distribution')
@importer_required
def distribution_create(request):
    """ثبت توزیع جدید"""
    if request.method == 'POST':
        form = ImportToDistributorForm(request.POST, user=request.user.owner)
        if form.is_valid():
            distribution = form.save(commit=False)
            distribution.distributor_company = distribution.distributor.distribution_profile.company
            distribution.save()

            # به‌روزرسانی وضعیت ورود اگر تمام مقدار توزیع شده باشد
            import_record = distribution.fuel_import
            if import_record.remaining_amount <= 0:
                import_record.status = 'distributed'
                import_record.save()

            messages.success(request, 'توزیع با موفقیت ثبت شد.')
            return redirect('fuel_distribution:distribution_detail', pk=distribution.pk)
    else:
        form = ImportToDistributorForm(user=request.user.owner)
        # فیلتر کردن ورودهایی که مقداری برای توزیع دارند
        form.fields['fuel_import'].queryset = SuperFuelImport.objects.filter(
            importer=request.user.owner,
            status__in=['confirmed', 'distributed']
        ).exclude(remaining_amount=0)

    context = {
        'form': form,
        'title': 'ثبت توزیع جدید'
    }
    return TemplateResponse(request, 'fuel_distribution/distributions/create.html', context)


@cache_permission('fuel_distribution')
@importer_required
def distribution_detail(request, pk):
    """جزئیات یک توزیع"""
    distribution = get_object_or_404(
        ImportToDistributor,
        pk=pk,
        fuel_import__importer=request.user.owner
    )

    # توزیع‌های این محموله به جایگاه‌ها
    station_distributions = distribution.station_distributions.all()

    context = {
        'distribution': distribution,
        'station_distributions': station_distributions
    }
    return TemplateResponse(request, 'fuel_distribution/distributions/detail.html', context)


# ============================
# View های توزیع‌کننده
# ============================

@cache_permission('fuel_distribution')
@distributor_required
def received_fuel_list(request):
    """لیست بنزین دریافتی توسط توزیع‌کننده"""
    received_fuel = ImportToDistributor.objects.filter(
        distributor=request.user.owner
    ).order_by('-distribution_date')

    # فیلترها
    importer_filter = request.GET.get('importer', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if importer_filter:
        received_fuel = received_fuel.filter(fuel_import__importer_id=importer_filter)
    if date_from:
        received_fuel = received_fuel.filter(distribution_date__gte=date_from)
    if date_to:
        received_fuel = received_fuel.filter(distribution_date__lte=date_to)

    # صفحه‌بندی
    paginator = Paginator(received_fuel, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # محاسبه موجودی
    stock = FuelStock.objects.filter(company=request.user.owner.distribution_profile.company).first()

    context = {
        'received_fuel': page_obj,
        'stock': stock,
        'importer_filter': importer_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/received_fuel.html', context)


@cache_permission('fuel_distribution')
@distributor_required
def distributor_stations(request):
    """لیست جایگاه‌های زیرمجموعه توزیع‌کننده"""
    stations = DistributorGasStation.objects.filter(
        distributor=request.user.owner,
        is_active=True
    ).order_by('gas_station__name')

    # آمار کلی
    total_stations = stations.count()
    active_stations = stations.filter(is_active=True).count()

    # توزیع‌های آخر به هر جایگاه
    for station in stations:
        station.last_delivery = DistributionToGasStation.objects.filter(
            distributor_gas_station=station,
            status='delivered'
        ).order_by('-delivery_date').first()

    context = {
        'stations': stations,
        'total_stations': total_stations,
        'active_stations': active_stations
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/stations.html', context)


@cache_permission('fuel_distribution')
@distributor_required
def station_create(request):
    """افزودن جایگاه جدید به زیرمجموعه"""
    if request.method == 'POST':
        _date = request.POST.get('start_date')
        _date = to_miladi(_date)
        form = DistributorGasStationForm(request.POST, distributor=request.user.owner)
        if form.is_valid():
            station = form.save(commit=False)
            station.start_date = _date
            station.distributor = request.user.owner
            station.save()

            messages.success(request, 'جایگاه با موفقیت به زیرمجموعه اضافه شد.')
            return redirect('fuel_distribution:distributor_stations')
    else:
        form = DistributorGasStationForm(distributor=request.user.owner)

    context = {
        'form': form,
        'title': 'افزودن جایگاه جدید'
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/station_create.html', context)


@cache_permission('fuel_distribution')
@distributor_required
def station_detail(request, pk):
    """جزئیات یک جایگاه زیرمجموعه"""
    station = get_object_or_404(
        DistributorGasStation,
        pk=pk,
        distributor=request.user.owner
    )

    # تاریخچه توزیع به این جایگاه
    deliveries = DistributionToGasStation.objects.filter(
        distributor_gas_station=station
    ).order_by('-delivery_date')

    # آمار کلی
    total_delivered = deliveries.filter(status='delivered').aggregate(
        total=Sum('amount_liters')
    )['total'] or 0

    pending_deliveries = deliveries.filter(status='scheduled').count()

    context = {
        'station': station,
        'deliveries': deliveries,
        'total_delivered': total_delivered,
        'pending_deliveries': pending_deliveries
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/station_detail.html', context)


@cache_permission('fuel_distribution')
@distributor_required
def delivery_to_station_create(request, station_id=None):
    """ثبت توزیع به جایگاه"""
    station = None
    if station_id:
        station = get_object_or_404(
            DistributorGasStation,
            pk=station_id,
            distributor=request.user.owner
        )

    if request.method == 'POST':
        _date = request.POST.get('delivery_date')
        _date = to_miladi(_date)

        form = DistributionToGasStationForm(
            request.POST,
            distributor=request.user.owner,
            station=station
        )
        if form.is_valid():
            print(form.cleaned_data)
            delivery = form.save(commit=False)
            delivery.delivery_date = _date
            a = delivery.save()
            print(delivery.distributor_gas_station.gas_station)

            try:
                mojodi = SupplierTankInventory.objects.get(supermodel=delivery.distributor_gas_station.gas_station)

                mojodi.actual_quantity += delivery.amount_liters
                mojodi.calculated_quantity += delivery.amount_liters
                mojodi.save()

            except SupplierTankInventory.DoesNotExist:
                SupplierTankInventory.objects.create(supermodel=delivery.distributor_gas_station.gas_station,
                                                     product_id=3, tank_date=delivery.delivery_date,
                                                     actual_quantity=delivery.amount_liters,
                                                     calculated_quantity=delivery.amount_liters)

            messages.success(request, 'توزیع به جایگاه با موفقیت ثبت شد.')

            if station_id:
                return redirect('fuel_distribution:station_detail', pk=station_id)
            else:
                return redirect('fuel_distribution:delivery_list')
    else:
        form = DistributionToGasStationForm(
            distributor=request.user.owner,
            station=station
        )

    context = {
        'form': form,
        'title': 'ثبت توزیع به جایگاه',
        'station': station
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/delivery_create.html', context)


@cache_permission('fuel_distribution')
@distributor_required
def delivery_list(request):
    """لیست توزیع‌های انجام شده به جایگاه‌ها"""
    deliveries = DistributionToGasStation.objects.filter(
        distributor_gas_station__distributor=request.user.owner
    ).order_by('-delivery_date')

    # فیلترها
    status_filter = request.GET.get('status', '')
    station_filter = request.GET.get('station', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    if station_filter:
        deliveries = deliveries.filter(distributor_gas_station_id=station_filter)
    if date_from:
        deliveries = deliveries.filter(delivery_date__gte=date_from)
    if date_to:
        deliveries = deliveries.filter(delivery_date__lte=date_to)

    # صفحه‌بندی
    paginator = Paginator(deliveries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # لیست جایگاه‌ها برای فیلتر
    stations = DistributorGasStation.objects.filter(
        distributor=request.user.owner
    ).values('id', 'gas_station__name')

    context = {
        'deliveries': page_obj,
        'stations': stations,
        'status_filter': status_filter,
        'station_filter': station_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/deliveries.html', context)


@distributor_required
@require_POST
def delivery_confirm(request, pk):
    """تأیید تحویل به جایگاه"""
    delivery = get_object_or_404(
        DistributionToGasStation,
        pk=pk,
        distributor_gas_station__distributor=request.user.owner,
        status='in_transit'
    )

    delivery.status = 'delivered'
    delivery.received_confirmation = True
    delivery.received_date = timezone.now().date()
    delivery.save()

    messages.success(request, 'تحویل با موفقیت تأیید شد.')
    return redirect('fuel_distribution:delivery_detail', pk=pk)


@cache_permission('fuel_distribution')
@distributor_required
def delivery_detail(request, pk):
    """جزئیات یک توزیع به جایگاه"""
    delivery = get_object_or_404(
        DistributionToGasStation,
        pk=pk,
        distributor_gas_station__distributor=request.user.owner
    )

    context = {
        'delivery': delivery
    }
    return TemplateResponse(request, 'fuel_distribution/distributor/delivery_detail.html', context)


# ============================
# View های گزارش‌گیری
# ============================

@cache_permission('fuel_distribution')
def reports_dashboard(request):
    """داشبورد گزارش‌ها"""
    profile = getattr(request.user.owner, 'distribution_profile', None)

    if not profile:
        messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
        return redirect('fuel_distribution:profile_create')

    context = {
        'profile': profile,
        'role': profile.role if profile else None
    }
    return TemplateResponse(request, 'fuel_distribution/reports/dashboard.html', context)


@cache_permission('fuel_distribution')
def generate_import_report_view(request):
    """ایجاد گزارش واردات"""
    if not hasattr(request.user.owner, 'distribution_profile'):
        messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
        return redirect('fuel_distribution:profile_create')

    if request.method == 'POST':
        form = FuelDistributionReportForm(request.POST, user=request.user.owner)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            period_start = form.cleaned_data['period_start']
            period_end = form.cleaned_data['period_end']
            company = form.cleaned_data.get('company')

            # تولید گزارش بر اساس نوع
            if report_type == 'imports':
                report_data = generate_import_report(
                    request.user.owner, period_start, period_end, company
                )
            elif report_type == 'distributions':
                report_data = generate_distribution_report(
                    request.user.owner, period_start, period_end, company
                )
            elif report_type == 'stock':
                report_data = generate_stock_report(
                    request.user.owner, period_start, period_end, company
                )
            else:
                messages.error(request, 'نوع گزارش نامعتبر است.')
                return redirect('fuel_distribution:reports_dashboard')

            # ذخیره گزارش
            report = FuelDistributionReport.objects.create(
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                company=company,
                generated_by=request.user.owner,
                report_data=report_data
            )

            messages.success(request, 'گزارش با موفقیت تولید شد.')
            return redirect('fuel_distribution:report_detail', pk=report.pk)
    else:
        form = FuelDistributionReportForm(user=request.user.owner)

    context = {
        'form': form,
        'title': 'تولید گزارش'
    }
    return TemplateResponse(request, 'fuel_distribution/reports/generate_report.html', context)


@cache_permission('fuel_distribution')
def report_list(request):
    """لیست گزارش‌های تولید شده"""
    reports = FuelDistributionReport.objects.filter(
        generated_by=request.user.owner
    ).order_by('-created_at')

    context = {
        'reports': reports
    }
    return TemplateResponse(request, 'fuel_distribution/reports/list.html', context)


@cache_permission('fuel_distribution')
def report_detail(request, pk):
    """جزئیات یک گزارش"""
    report = get_object_or_404(
        FuelDistributionReport,
        pk=pk,
        generated_by=request.user.owner
    )

    context = {
        'report': report
    }
    return TemplateResponse(request, 'fuel_distribution/reports/detail.html', context)


# ============================
# API Views برای AJAX
# ============================


@require_GET
def get_import_remaining_amount(request, import_id):
    """دریافت مقدار باقی‌مانده از یک ورود"""
    try:
        import_record = SuperFuelImport.objects.get(
            id=import_id,
            importer=request.user.owner
        )
        return JsonResponse({
            'remaining_amount': import_record.remaining_amount,
            'status': 'success'
        })
    except SuperFuelImport.DoesNotExist:
        return JsonResponse({
            'error': 'ورود یافت نشد',
            'status': 'error'
        }, status=404)


@require_GET
def get_distributor_stock(request):
    """دریافت موجودی توزیع‌کننده"""
    try:
        profile = request.user.owner.distribution_profile
        if profile.role != 'distributor':
            return JsonResponse({
                'error': 'دسترسی غیرمجاز',
                'status': 'error'
            }, status=403)

        stock = FuelStock.objects.filter(company=profile.company).first()
        if stock:
            return JsonResponse({
                'current_stock': stock.current_stock,
                'total_imported': stock.total_imported,
                'total_distributed': stock.total_distributed,
                'status': 'success'
            })
        else:
            return JsonResponse({
                'current_stock': 0,
                'total_imported': 0,
                'total_distributed': 0,
                'status': 'success'
            })
    except UserDistributionProfile.DoesNotExist:
        return JsonResponse({
            'error': 'پروفایل یافت نشد',
            'status': 'error'
        }, status=404)


@require_GET
def search_distributors(request):
    """جستجوی توزیع‌کننده‌ها"""
    query = request.GET.get('q', '')

    if query:
        distributors = Owner.objects.filter(
            distribution_profile__role='distributor'
        ).values('id', 'name', 'lname', 'codemeli', 'distribution_profile__company__name')[:10]
    else:
        distributors = []

    return JsonResponse({
        'distributors': list(distributors),
        'status': 'success'
    })


@require_GET
def search_gas_stations(request):
    """جستجوی جایگاه‌ها"""
    query = request.GET.get('q', '')

    if query:
        stations = SuperModel.objects.filter(
            Q(name__icontains=query) |
            Q(gsid__icontains=query) |
            Q(address__icontains=query)
        ).values('id', 'name', 'gsid', 'address')[:10]
    else:
        stations = []

    return JsonResponse({
        'stations': list(stations),
        'status': 'success'
    })


# ============================
# View های مدیریت موجودی
# ============================

@cache_permission('fuel_distribution')
def stock_management(request):
    """مدیریت موجودی"""
    profile = getattr(request.user.owner, 'distribution_profile', None)

    if not profile:
        messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
        return redirect('fuel_distribution:profile_create')

    stock = FuelStock.objects.filter(company=profile.company).first()

    if request.method == 'POST':
        form = FuelStockUpdateForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'موجودی با موفقیت به‌روزرسانی شد.')
            return redirect('fuel_distribution:stock_management')
    else:
        form = FuelStockUpdateForm(instance=stock)

    context = {
        'stock': stock,
        'form': form,
        'profile': profile
    }
    return TemplateResponse(request, 'fuel_distribution/stock/management.html', context)


@cache_permission('fuel_distribution')
def stock_history(request):
    """تاریخچه موجودی"""
    profile = getattr(request.user.owner, 'distribution_profile', None)

    if not profile:
        messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
        return redirect('fuel_distribution:profile_create')

    # تاریخچه 30 روز گذشته
    thirty_days_ago = timezone.now() - timedelta(days=30)

    if profile.role == 'importer':
        imports = SuperFuelImport.objects.filter(
            importer=request.user.owner,
            import_date__gte=thirty_days_ago
        ).order_by('import_date')

        distributions = ImportToDistributor.objects.filter(
            fuel_import__importer=request.user.owner,
            distribution_date__gte=thirty_days_ago
        ).order_by('distribution_date')

        context = {
            'imports': imports,
            'distributions': distributions,
            'role': 'importer'
        }

    elif profile.role == 'distributor':
        received = ImportToDistributor.objects.filter(
            distributor=request.user.owner,
            distribution_date__gte=thirty_days_ago
        ).order_by('distribution_date')

        delivered = DistributionToGasStation.objects.filter(
            distributor_gas_station__distributor=request.user.owner,
            delivery_date__gte=thirty_days_ago
        ).order_by('delivery_date')

        context = {
            'received': received,
            'delivered': delivered,
            'role': 'distributor'
        }

    else:
        context = {'role': 'gas_station'}

    return TemplateResponse(request, 'fuel_distribution/stock/history.html', context)


@cache_permission('fuel_distribution')
@importer_required
def distribution_create(request):
    """ثبت توزیع جدید"""
    if request.method == 'POST':
        _date = request.POST.get('distribution_date')
        _date = to_miladi(_date)
        form = ImportToDistributorForm(request.POST, user=request.user.owner)
        if form.is_valid():
            distribution = form.save(commit=False)
            distribution.distribution_date = _date
            distribution.distributor_company = distribution.distributor.distribution_profile.company
            distribution.save()

            # به‌روزرسانی وضعیت ورود اگر تمام مقدار توزیع شده باشد
            import_record = distribution.fuel_import
            if import_record.remaining_amount <= 0:
                import_record.status = 'distributed'
                import_record.save()

            messages.success(request, 'توزیع با موفقیت ثبت شد.')
            return redirect('fuel_distribution:distribution_detail', pk=distribution.pk)
    else:
        form = ImportToDistributorForm(user=request.user)
        # فیلتر کردن ورودهایی که مقداری برای توزیع دارند
        form.fields['fuel_import'].queryset = SuperFuelImport.objects.filter(
            importer=request.user.owner,
            status__in=['confirmed', 'distributed']
        ).annotate(
            distributed_total=Coalesce(Sum('distributions__amount_liters'), 0, output_field=FloatField())
        ).annotate(
            remaining=F('amount_liters') - F('distributed_total')
        ).filter(
            remaining__gt=0  # فقط آنهایی که باقی‌مانده دارند
        )

    context = {
        'form': form,
        'title': 'ثبت توزیع جدید'
    }
    return TemplateResponse(request, 'fuel_distribution/distributions/create.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def supplier_dashboard(request):
    """داشبورد عرضه کننده"""
    profile = request.user.owner.distribution_profile

    # دریافت جایگاه انتخابی فعلی
    current_station_id = request.session.get('current_station_id')

    if current_station_id:
        try:
            current_station = SuperModel.objects.get(id=current_station_id)
            # بررسی دسترسی کاربر به این جایگاه
            if not profile.can_manage_station(current_station):
                current_station = None
        except SuperModel.DoesNotExist:
            current_station = None
    else:
        current_station = None

    # اگر جایگاه انتخابی نداریم، اولین جایگاه را انتخاب کنیم
    if not current_station and profile.managed_stations.exists():
        current_station = profile.managed_stations.first()
        request.session['current_station_id'] = current_station.id
        request.session['current_station_name'] = current_station.name

    if not current_station:
        messages.error(request, 'شما هیچ جایگاهی برای مدیریت ندارید.')
        return redirect('fuel_distribution:profile_create')

    # آمار امروز برای جایگاه انتخابی
    today = timezone.now().date()

    # فروش امروز
    today_sales = NozzleSale.objects.filter(
        supermodel=current_station,
        sale_date=today,
        status='confirmed'
    ).aggregate(
        total_liters=Sum('sold_liters'),
        total_amount=Sum('total_amount')
    )

    # تحویل‌های در انتظار تأیید
    pending_deliveries = DistributionToGasStation.objects.filter(
        distributor_gas_station__gas_station=current_station,
        status='delivered'
    ).count()

    # موجودی فعلی
    last_inventory = SupplierTankInventory.objects.filter(
        supermodel=current_station
    ).order_by('-tank_date').first()

    # نرخ‌های امروز
    today_prices = DailyProductPrice.objects.filter(
        supermodel=current_station,
        price_date=today,
        is_active=True
    )

    # لیست همه جایگاه‌های تحت مدیریت
    managed_stations = profile.managed_stations.all()

    context = {
        'profile': profile,
        'current_station': current_station,
        'managed_stations': managed_stations,
        'today': today,
        'today_sales': today_sales,
        'pending_deliveries': pending_deliveries,
        'last_inventory': last_inventory,
        'today_prices': today_prices,
        'role': 'gas_station'
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/dashboard.html', context)


# تابع کمکی برای دریافت جایگاه فعلی
def get_current_station(request):
    """دریافت جایگاه انتخابی فعلی کاربر"""
    profile = getattr(request.user.owner, 'distribution_profile', None)

    if not profile or profile.role != 'gas_station':
        return None

    current_station_id = request.session.get('current_station_id')

    if current_station_id:
        try:
            station = SuperModel.objects.get(id=current_station_id)
            if profile.can_manage_station(station):
                return station
        except SuperModel.DoesNotExist:
            pass

    # اگر جایگاه معتبر نداریم، اولین جایگاه را برگردان
    if profile.managed_stations.exists():
        station = profile.managed_stations.first()
        request.session['current_station_id'] = station.id
        request.session['current_station_name'] = station.name
        return station

    return None


@cache_permission('fuel_distribution')
@gas_station_required
def daily_price_management(request):
    """مدیریت نرخ روزانه فرآورده‌ها"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    current_station = get_current_station(request)

    if not current_station:
        messages.error(request, 'جایگاه انتخابی معتبر نیست.')
        return redirect('fuel_distribution:supplier_dashboard')

    today = timezone.now().date()

    if request.method == 'POST':
        # دریافت نرخ‌های ارسالی
        product_prices = {}

        for key, value in request.POST.items():
            if key.startswith('price_'):
                product_id = key.split('_')[1]
                if value:
                    try:
                        product_prices[int(product_id)] = int(value)
                    except ValueError:
                        continue

        # ذخیره نرخ‌ها
        for product_id, price in product_prices.items():
            DailyProductPrice.objects.update_or_create(
                supermodel=supermodel,
                product_id=product_id,
                price_date=today,
                defaults={
                    'price_per_liter': price,
                    'is_active': True
                }
            )

        messages.success(request, 'نرخ‌های روزانه با موفقیت ثبت شدند.')
        return redirect('fuel_distribution:supplier_dashboard')

    # لیست فرآورده‌های عرضه کننده
    products = Product.objects.filter(
        nazel__supermodel=supermodel
    ).distinct()

    # نرخ‌های امروز
    today_prices = DailyProductPrice.objects.filter(
        supermodel=supermodel,
        price_date=today
    )

    price_dict = {price.product_id: price.price_per_liter for price in today_prices}

    context = {
        'supermodel': supermodel,
        'products': products,
        'today': today,
        'price_dict': price_dict
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/daily_price.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def nozzle_sales_management(request):
    """مدیریت فروش نازل‌ها"""

    current_station = get_current_station(request)

    if not current_station:
        messages.error(request, 'جایگاه انتخابی معتبر نیست.')
        return redirect('fuel_distribution:supplier_dashboard')

    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    today = timezone.now().date()

    if request.method == 'POST':
        sale_date_str = request.POST.get('sale_date')
        sale_date = to_miladi(sale_date_str) if sale_date_str else today

        # دریافت داده‌های هر نازل
        nozzle_data = []

        for key, value in request.POST.items():
            if key.startswith('nozzle_'):
                parts = key.split('_')

                if len(parts) >= 3:
                    nozzle_id = parts[1]
                    field = parts[2]

                    # پیدا کردن یا ایجاد ورودی برای این نازل
                    nozzle_entry = next((x for x in nozzle_data if x['id'] == nozzle_id), None)
                    if not nozzle_entry:
                        nozzle_entry = {'id': nozzle_id}
                        nozzle_data.append(nozzle_entry)

                    nozzle_entry[field] = value

        # ذخیره فروش‌های نازل
        for data in nozzle_data:
            if 'start' in data and 'end' in data and data['start'] and data['end']:
                try:
                    nozzle = Nazel.objects.get(id=data['id'], supermodel=supermodel)

                    # یافتن نرخ روزانه
                    price = DailyProductPrice.objects.filter(
                        supermodel=supermodel,
                        product=nozzle.product,
                        is_active=True
                    ).last()

                    if not price:
                        messages.error(request, f'برای نازل {nozzle.number} نرخ روزانه تعریف نشده است.')
                        continue

                    # محاسبه فروش (با کسر میزان آزمایش)
                    start_counter = int(data['start'])
                    end_counter = int(data['end'])
                    test_amount = int(data.get('test', 0))

                    if end_counter >= start_counter:
                        raw_liters = end_counter - start_counter
                    else:
                        max_counter = 999999
                        raw_liters = (max_counter - start_counter) + end_counter

                    sold_liters = max(0, raw_liters - test_amount)

                    # ایجاد یا به‌روزرسانی فروش نازل
                    NozzleSale.objects.update_or_create(
                        nozzle=nozzle,
                        sale_date=sale_date,
                        defaults={
                            'supermodel': supermodel,
                            'start_counter': start_counter,
                            'end_counter': end_counter,
                            'test_amount': test_amount,
                            'sold_liters': sold_liters,
                            'price_per_liter': price.price_per_liter,
                            'total_amount': sold_liters * price.price_per_liter,
                            'status': 'confirmed'
                        }
                    )

                except Exception as e:
                    messages.error(request, f'خطا در ثبت فروش نازل: {str(e)}')

        messages.success(request, 'فروش نازل‌ها با موفقیت ثبت شد.')
        return redirect('fuel_distribution:nozzle_sales_list')

    # لیست نازل‌های عرضه کننده
    nozzles = Nazel.objects.filter(supermodel=supermodel)

    # فروش‌های امروز برای پیش‌پر کردن فرم
    today_sales = NozzleSale.objects.filter(
        supermodel=supermodel,
        sale_date=today
    )
    sales_dict = {sale.nozzle_id: sale for sale in today_sales}

    context = {
        'supermodel': supermodel,
        'nozzles': nozzles,
        'today': today,
        'sales_dict': sales_dict
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/nozzle_sales.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def tank_inventory_management(request):
    """مدیریت موجودی واقعی مخزن"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    today = timezone.now().date()

    if request.method == 'POST':
        tank_date_str = request.POST.get('tank_date')

        # دریافت موجودی واقعی هر فرآورده
        for product in Product.objects.filter(nazel__supermodel=supermodel).distinct():
            actual_key = f'actual_{product.id}'
            actual_value = request.POST.get(actual_key)

            if actual_value:
                try:
                    actual_quantity = int(actual_value)

                    # ذخیره موجودی واقعی
                    _supplire = SupplierTankInventory.objects.get(supermodel=supermodel,
                                                                  product=product)
                    _supplire.actual_quantity = actual_quantity
                    _supplire.calculated_quantity = actual_quantity
                    _supplire.save()




                except ValueError:
                    messages.error(request, f'مقدار نامعتبر برای {product.name}')

        messages.success(request, 'موجودی واقعی مخزن با موفقیت ثبت شد.')
        return redirect('fuel_distribution:inventory_history')

    # آخرین موجودی واقعی برای پیش‌پر کردن فرم
    last_inventory = SupplierTankInventory.objects.filter(
        supermodel=supermodel
    ).order_by('-tank_date').first()

    context = {
        'supermodel': supermodel,
        'today': today,
        'last_inventory': last_inventory
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/tank_inventory.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def delivery_receipt(request, pk):
    """تأیید دریافت تحویل از توزیع‌کننده"""
    delivery = get_object_or_404(
        DistributionToGasStation,
        pk=pk,
        distributor_gas_station__gas_station__owner=request.user.owner
    )

    if request.method == 'POST':
        receipt_number = request.POST.get('receipt_number')
        received_date_str = request.POST.get('received_date')
        received_date = to_miladi(received_date_str) if received_date_str else timezone.now().date()
        notes = request.POST.get('notes', '')

        # به‌روزرسانی وضعیت به "دریافت شده"
        delivery.status = 'received'
        delivery.station_receipt_number = receipt_number
        delivery.station_received_date = received_date
        delivery.station_received_by = request.user.owner
        delivery.station_notes = notes
        delivery.save()

        messages.success(request, 'تحویل با موفقیت تأیید و رسید صادر شد.')
        return redirect('fuel_distribution:pending_deliveries')

    context = {
        'delivery': delivery
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/delivery_receipt.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def pending_deliveries(request):
    """لیست تحویل‌های در انتظار تأیید"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    deliveries = DistributionToGasStation.objects.filter(
        distributor_gas_station__gas_station=supermodel,
        status='delivered'  # تحویل شده اما تأیید نشده توسط جایگاه
    ).order_by('-delivery_date')

    context = {
        'deliveries': deliveries,
        'supermodel': supermodel
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/pending_deliveries.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def daily_summary(request):
    """خلاصه روزانه فعالیت‌ها"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    # تاریخ پیش‌فرض: امروز
    date_str = request.GET.get('date', '')
    selected_date = to_miladi(date_str) if date_str else timezone.now().date()

    # خلاصه روز انتخاب شده
    summary = SupplierDailySummary.objects.filter(
        supermodel=supermodel,
        summary_date=selected_date
    ).first()

    # فروش‌های روز
    sales = NozzleSale.objects.filter(
        supermodel=supermodel,
        sale_date=selected_date,
        status='confirmed'
    )

    # تحویل‌های دریافتی در این روز
    deliveries = DistributionToGasStation.objects.filter(
        distributor_gas_station__gas_station=supermodel,
        station_received_date=selected_date,
        status='received'
    )

    # موجودی واقعی روز
    inventory = SupplierTankInventory.objects.filter(
        supermodel=supermodel,
        tank_date=selected_date
    ).first()

    context = {
        'supermodel': supermodel,
        'selected_date': selected_date,
        'summary': summary,
        'sales': sales,
        'deliveries': deliveries,
        'inventory': inventory
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/daily_summary.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def nozzle_sales_list(request):
    """لیست فروش‌های نازل"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    sales = NozzleSale.objects.filter(
        supermodel=supermodel
    ).order_by('-sale_date', 'nozzle__number')

    # فیلترها
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status_filter = request.GET.get('status', '')
    try:
        date_from = to_miladi(date_from)
        date_to = to_miladi(date_to)
    except ValueError:
        pass
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)
    if status_filter:
        sales = sales.filter(status=status_filter)

    context = {
        'sales': sales,
        'date_from': date_from,
        'date_to': date_to,
        'status_filter': status_filter
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/nozzle_sales_list.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def inventory_history(request):
    """تاریخچه موجودی مخازن"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        messages.error(request, 'عرضه کننده مرتبط با شما یافت نشد.')
        return redirect('fuel_distribution:profile_create')

    inventories = SupplierTankInventory.objects.filter(
        supermodel=supermodel
    ).order_by('-tank_date')

    # فیلترها
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')

    if date_from:
        inventories = inventories.filter(tank_date__gte=date_from)
    if date_to:
        inventories = inventories.filter(tank_date__lte=date_to)
    if product_filter:
        inventories = inventories.filter(product_id=product_filter)

    context = {
        'inventories': inventories,
        'date_from': date_from,
        'date_to': date_to,
        'product_filter': product_filter
    }
    return TemplateResponse(request, 'fuel_distribution/supplier/inventory_history.html', context)


# ============================
# API Views برای AJAX
# ============================

@require_GET
@gas_station_required
def get_daily_summary_ajax(request):
    """دریافت خلاصه روزانه به صورت AJAX"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        return JsonResponse({'error': 'عرضه کننده یافت نشد'}, status=404)

    date_str = request.GET.get('date', '')
    selected_date = to_miladi(date_str) if date_str else timezone.now().date()

    summary = SupplierDailySummary.objects.filter(
        supermodel=supermodel,
        summary_date=selected_date
    ).first()

    if summary:
        data = {
            'opening_inventory': summary.opening_inventory,
            'closing_inventory': summary.closing_inventory,
            'calculated_closing': summary.calculated_closing,
            'difference': summary.difference,
            'total_sales_liters': summary.total_sales_liters,
            'total_sales_amount': summary.total_sales_amount
        }
    else:
        data = {
            'opening_inventory': 0,
            'closing_inventory': 0,
            'calculated_closing': 0,
            'difference': 0,
            'total_sales_liters': 0,
            'total_sales_amount': 0
        }

    return JsonResponse({'status': 'success', 'data': data})


@require_GET
@gas_station_required
def get_today_prices_ajax(request):
    """دریافت نرخ‌های امروز به صورت AJAX"""
    supermodel = SuperModel.objects.filter(owner=request.user.owner).first()

    if not supermodel:
        return JsonResponse({'error': 'عرضه کننده یافت نشد'}, status=404)

    today = timezone.now().date()
    prices = DailyProductPrice.objects.filter(
        supermodel=supermodel,
        price_date=today,
        is_active=True
    ).values('product_id', 'product__name', 'price_per_liter')

    return JsonResponse({
        'status': 'success',
        'prices': list(prices)
    })


@require_GET
@gas_station_required
def get_nozzle_last_counter_ajax(request, nozzle_id):
    """دریافت آخرین شمارشگر نازل"""
    try:
        nozzle = Nazel.objects.get(id=nozzle_id)
        last_sale = NozzleSale.objects.filter(
            nozzle=nozzle,
            status='confirmed'
        ).order_by('-sale_date', '-end_counter').first()

        if last_sale:
            last_counter = last_sale.end_counter
        else:
            last_counter = 0

        return JsonResponse({
            'status': 'success',
            'last_counter': last_counter,
            'nozzle_number': nozzle.number,
            'product_name': nozzle.product.name
        })
    except Nazel.DoesNotExist:
        return JsonResponse({'error': 'نازل یافت نشد'}, status=404)


@login_required
@gas_station_required
@require_POST
def change_current_station(request):
    """تغییر جایگاه انتخابی فعلی کاربر"""
    station_id = request.POST.get('station_id')

    try:
        profile = request.user.owner.distribution_profile
        station = SuperModel.objects.get(id=station_id)

        # بررسی اینکه کاربر مجاز به مدیریت این جایگاه است
        if not profile.can_manage_station(station):
            messages.error(request, 'شما مجوز مدیریت این جایگاه را ندارید.')
            return redirect('fuel_distribution:supplier_dashboard')

        # ذخیره جایگاه انتخابی در session
        request.session['current_station_id'] = station_id
        request.session['current_station_name'] = station.name

        messages.success(request, f'جایگاه فعلی به "{station.name}" تغییر کرد.')

    except SuperModel.DoesNotExist:
        messages.error(request, 'جایگاه یافت نشد.')

    return redirect('fuel_distribution:supplier_dashboard')


# در views.py اضافه کنید

@login_required
@gas_station_required
@require_POST
def set_active_station(request, station_id):
    """تنظیم جایگاه فعال در پروفایل کاربر"""
    try:
        profile = request.user.owner.distribution_profile
        station = SuperModel.objects.get(id=station_id)

        # بررسی اینکه آیا این جایگاه متعلق به کاربر است
        if not profile.can_manage_station(station):
            messages.error(request, 'شما مجوز مدیریت این جایگاه را ندارید.')
            return redirect('fuel_distribution:user_profile')

        # تنظیم جایگاه فعال
        profile.active_station = station
        profile.save()

        # به‌روزرسانی session
        request.session['current_station_id'] = station.id
        request.session['current_station_name'] = station.name

        messages.success(request, f'جایگاه فعال به "{station.name}" تغییر کرد.')

    except SuperModel.DoesNotExist:
        messages.error(request, 'جایگاه یافت نشد.')

    return redirect('fuel_distribution:user_profile')


@login_required
@gas_station_required
@require_POST
def quick_change_station(request):
    """تغییر سریع جایگاه فعال از فرم dropdown"""
    station_id = request.POST.get('station_id')

    if not station_id:
        messages.error(request, 'لطفاً جایگاهی را انتخاب کنید.')
        return redirect('fuel_distribution:user_profile')

    return set_active_station(request, station_id)


@cache_permission('fuel_distribution')
def management_sales_report(request):
    """گزارش مدیریتی فروش جایگاه‌ها"""

    # دریافت پارامترهای فیلتر
    stations_list=None
    total_summary=0
    period_start=''
    period_end=''
    period_start_str2 = request.GET.get('period_start', '')
    period_end_str2 = request.GET.get('period_end', '')
    area_filter = request.GET.get('area', '')
    period_start_str = request.GET.get('period_start', '')
    period_end_str = request.GET.get('period_end', '')
    try:
        period_start = to_miladi(period_start_str)
        period_end = to_miladi(period_end_str)

        # فیلتر پایه فروش‌ها
        sales_filter = Q(
            sale_date__gte=period_start,
            sale_date__lte=period_end,
            status='confirmed'
        )

        # اگر کاربر نقش جایگاه دارد، فقط جایگاه‌های تحت مدیریتش را ببینید
        profile = request.user.owner.distribution_profile
        if profile.role == 'gas_station' and profile.managed_stations.exists():
            managed_station_ids = profile.managed_stations.values_list('id', flat=True)
            sales_filter &= Q(supermodel_id__in=managed_station_ids)
        elif request.user.owner.role.role == 'zone':
            sales_filter &= Q(supermodel__area__zone_id=request.user.owner.zone.id)

        elif request.user.owner.role.role == 'engin':
            sales_filter &= Q(supermodel__area__zone_id=request.user.owner.zone.id)

        elif request.user.owner.role.role == 'area':
            sales_filter &= Q(supermodel__area_id=request.user.owner.id)

        # فیلتر منطقه
        if area_filter:
            sales_filter &= Q(supermodel__area_id=area_filter)

        # جمع‌آوری داده‌های فروش
        sales_data = NozzleSale.objects.filter(sales_filter).values(
            'supermodel__id',
            'supermodel__name',
            'supermodel__gsid',
            'supermodel__address',
            'supermodel__phone',
            'supermodel__area__name',
            'sale_date'
        ).annotate(
            daily_sold_liters=Sum('sold_liters'),
            daily_test_liters=Sum('test_amount'),
            daily_sales_amount=Sum('total_amount'),
            daily_transactions=Count('id')
        ).order_by('supermodel__name', 'sale_date')

        # گروه‌بندی بر اساس جایگاه
        stations_summary = {}
        for sale in sales_data:
            station_id = sale['supermodel__id']

            if station_id not in stations_summary:
                stations_summary[station_id] = {
                    'station_id': station_id,
                    'station_name': sale['supermodel__name'],
                    'station_gsid': sale['supermodel__gsid'],
                    'station_address': sale['supermodel__address'],
                    'station_phone': sale['supermodel__phone'],
                    'area_name': sale['supermodel__area__name'] or 'تعریف نشده',
                    'total_sales_liters': 0,
                    'total_test_liters': 0,
                    'total_sales_amount': 0,
                    'total_transactions': 0,
                    'active_days': set(),  # برای شمارش روزهای فعال
                    'daily_data': []  # داده‌های روزانه
                }

            # اضافه کردن به مجموع
            station = stations_summary[station_id]
            station['total_sales_liters'] += sale['daily_sold_liters'] or 0
            station['total_test_liters'] += sale['daily_test_liters'] or 0
            station['total_sales_amount'] += sale['daily_sales_amount'] or 0
            station['total_transactions'] += sale['daily_transactions'] or 0
            station['active_days'].add(sale['sale_date'])

            # ذخیره داده روزانه
            station['daily_data'].append({
                'date': sale['sale_date'],
                'sold_liters': sale['daily_sold_liters'] or 0,
                'test_liters': sale['daily_test_liters'] or 0,
                'sales_amount': sale['daily_sales_amount'] or 0,
                'transactions': sale['daily_transactions'] or 0
            })

        # تبدیل set به تعداد و محاسبه میانگین
        for station in stations_summary.values():
            station['active_days_count'] = len(station['active_days'])
            if station['active_days_count'] > 0:
                station['avg_daily_sales'] = round(station['total_sales_liters'] / station['active_days_count'], 2)
            else:
                station['avg_daily_sales'] = 0

            # حذف set برای جلوگیری از خطا در template
            del station['active_days']

        # مرتب‌سازی بر اساس فروش کل (بیشترین به کمترین)
        stations_list = sorted(
            stations_summary.values(),
            key=lambda x: x['total_sales_liters'],
            reverse=True
        )

        # محاسبه مجموع کل
        total_summary = {
            'total_stations': len(stations_list),
            'total_sales_liters': sum(s['total_sales_liters'] for s in stations_list),
            'total_test_liters': sum(s['total_test_liters'] for s in stations_list),
            'total_sales_amount': sum(s['total_sales_amount'] for s in stations_list),
            'total_transactions': sum(s['total_transactions'] for s in stations_list),
            'avg_sales_per_station': round(
                sum(s['total_sales_liters'] for s in stations_list) / len(stations_list) if stations_list else 0,
                2
            )
        }

    except:
        pass
    areas = Area.objects.all()

    context = {
        'stations': stations_list,
        'total_summary': total_summary,
        'period_start': period_start,
        'period_end': period_end,
        'period_start_str': period_start_str2 if period_start else '',
        'period_end_str': period_end_str2 if period_end else '',
        'areas': areas,
        'selected_area': area_filter,
        'report_title': f'گزارش فروش از {period_start} تا {period_end}'
    }

    return TemplateResponse(request, 'fuel_distribution/reports/management_sales_report.html', context)


@cache_permission('fuel_distribution')
@gas_station_required
def export_management_report(request):
    """خروجی اکسل گزارش مدیریتی"""
    # دریافت پارامترها از request
    period_start_str = request.GET.get('period_start', '')
    period_end_str = request.GET.get('period_end', '')
    area_filter = request.GET.get('area', '')

    # استفاده از منطق مشابه گزارش
    # (می‌توانید تابع generate_report_data را بسازید که داده‌ها را برگرداند)
    # برای سادگی، از همان منطق گزارش استفاده می‌کنیم

    # در اینجا کد خروجی اکسل مشابه قبلی قرار می‌گیرد
    # برای جلوگیری از تکرار، فقط اسکلت کد را می‌نویسم:

    import xlwt
    from django.http import HttpResponse
    import io

    # ایجاد workbook
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="management_report_{timezone.now().date()}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('گزارش مدیریتی فروش')

    # استایل‌ها
    header_style = xlwt.XFStyle()
    header_style.font.bold = True
    header_style.font.height = 280
    header_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    header_style.alignment.vert = xlwt.Alignment.VERT_CENTER

    # ... (کد کامل مشابه قبلی)

    # برای سادگی، می‌توانید داده‌ها را از تابع management_sales_report بگیرید
    # و در اکسل بگذارید

    wb.save(response)
    return response
