from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q, F, FloatField
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
import json
from datetime import timedelta

from .models import (
    UserDistributionProfile, SuperFuelImport, ImportToDistributor,
    DistributorGasStation, DistributionToGasStation, FuelStock,
    FuelDistributionReport
)
from base.models import GsModel, Owner, Company
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
        except UserDistributionProfile.DoesNotExist:
            messages.error(request, 'پروفایل توزیع برای شما تعریف نشده است.')
            return redirect('fuel_distribution:profile_create')

        return view_func(request, *args, **kwargs)

    return wrapper


# ============================
# View های عمومی
# ============================

@login_required
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

        return render(request, 'fuel_distribution/dashboard.html', context)

    except UserDistributionProfile.DoesNotExist:
        messages.info(request, 'لطفا پروفایل توزیع خود را تکمیل کنید.')
        return redirect('fuel_distribution:profile_create')


@login_required
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
    return render(request, 'fuel_distribution/profile/user_profile.html', context)


@login_required
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
    return render(request, 'fuel_distribution/profile/create_profile.html', context)


# ============================
# View های واردکننده
# ============================

@login_required
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
    return render(request, 'fuel_distribution/imports/list.html', context)


@login_required
@importer_required
def import_create(request):
    """ثبت واردات جدید"""
    if request.method == 'POST':
        form = SuperFuelImportForm(request.POST, user=request.user.owner)
        if form.is_valid():
            import_record = form.save(commit=False)
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
    return render(request, 'fuel_distribution/imports/create.html', context)


@login_required
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
    return render(request, 'fuel_distribution/imports/detail.html', context)


@login_required
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
    return render(request, 'fuel_distribution/imports/create.html', context)


@login_required
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

@login_required
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
    return render(request, 'fuel_distribution/distributions/list.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributions/create.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributions/detail.html', context)


# ============================
# View های توزیع‌کننده
# ============================

@login_required
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
    return render(request, 'fuel_distribution/distributor/received_fuel.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributor/stations.html', context)


@login_required
@distributor_required
def station_create(request):
    """افزودن جایگاه جدید به زیرمجموعه"""
    if request.method == 'POST':
        form = DistributorGasStationForm(request.POST, distributor=request.user.owner)
        if form.is_valid():
            station = form.save(commit=False)
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
    return render(request, 'fuel_distribution/distributor/station_create.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributor/station_detail.html', context)


@login_required
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
        form = DistributionToGasStationForm(
            request.POST,
            distributor=request.user.owner,
            station=station
        )
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.save()

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
    return render(request, 'fuel_distribution/distributor/delivery_create.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributor/deliveries.html', context)


@login_required
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


@login_required
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
    return render(request, 'fuel_distribution/distributor/delivery_detail.html', context)


# ============================
# View های گزارش‌گیری
# ============================

@login_required
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
    return render(request, 'fuel_distribution/reports/dashboard.html', context)


@login_required
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
    return render(request, 'fuel_distribution/reports/generate_report.html', context)


@login_required
def report_list(request):
    """لیست گزارش‌های تولید شده"""
    reports = FuelDistributionReport.objects.filter(
        generated_by=request.user.owner
    ).order_by('-created_at')

    context = {
        'reports': reports
    }
    return render(request, 'fuel_distribution/reports/list.html', context)


@login_required
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
    return render(request, 'fuel_distribution/reports/detail.html', context)


# ============================
# API Views برای AJAX
# ============================

@login_required
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


@login_required
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


@login_required
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


@login_required
@require_GET
def search_gas_stations(request):
    """جستجوی جایگاه‌ها"""
    query = request.GET.get('q', '')

    if query:
        stations = GsModel.objects.filter(
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

@login_required
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
    return render(request, 'fuel_distribution/stock/management.html', context)


@login_required
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

    return render(request, 'fuel_distribution/stock/history.html', context)


@login_required
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
    return render(request, 'fuel_distribution/distributions/create.html', context)