from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Q, Max
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from datetime import timedelta
import jdatetime

from accounts.logger import add_to_log
from base.permission_decoder import cache_permission
from base.templatetags.basefiltertag import to_md5
from sell.models import SellGs, SellModel, Waybill, Mojodi
from base.models import GsModel, Product, Zone


@cache_permission('dashboardsell')
def dashboard_main(request):
    """داشبورد اصلی"""
    context = {
        'page_title': 'داشبورد مدیریت فروش و موجودی',
        'zones': Zone.objects_limit.all(),
        'gs_list': GsModel.objects.none(),
        'products': Product.objects.all()
    }
    return TemplateResponse(request, 'main.html', context)


@login_required
def get_sales_data(request):
    """داده‌های فروش برای نمودارها"""
    days = int(request.GET.get('days', 7))
    product_id = request.GET.get('product_id')
    gs_id = request.GET.get('gs_id')

    # محاسبه تاریخ شروع
    end_date = jdatetime.date.today()
    start_date = end_date - timedelta(days=days)

    # فیلترها
    filters = Q(tarikh__gte=start_date, tarikh__lte=end_date)
    if product_id:
        filters &= Q(product_id=product_id)
    if gs_id:
        filters &= Q(gs_id=gs_id)
    print(product_id, gs_id, days)
    # داده‌های فروش
    sales_data = SellGs.objects.filter(filters).values('tarikh').annotate(
        total_sell=Sum('sell'),
        total_yarane=Sum('yarane'),
        total_azad=Sum('azad'),
        total_ezterari=Sum('ezterari')
    ).order_by('tarikh')

    # فرمت داده برای نمودار
    chart_data = {
        'labels': [],
        'datasets': [
            {'label': 'فروش کل', 'data': [], 'borderColor': '#4e73df', 'fill': False},
            {'label': 'یارانه‌ای', 'data': [], 'borderColor': '#1cc88a', 'fill': False},
            {'label': 'آزاد', 'data': [], 'borderColor': '#36b9cc', 'fill': False}
        ]
    }

    for item in sales_data:
        chart_data['labels'].append(item['tarikh'].strftime('%Y/%m/%d'))
        chart_data['datasets'][0]['data'].append(float(item['total_sell'] or 0))
        chart_data['datasets'][1]['data'].append(float(item['total_yarane'] or 0))
        chart_data['datasets'][2]['data'].append(float(item['total_azad'] or 0))

    return JsonResponse(chart_data)


@login_required
def get_inventory_data(request):
    """داده‌های موجودی و بارنامه"""
    gs_id = request.GET.get('gs_id')

    # فیلتر جایگاه
    filters = {}
    if gs_id:
        filters['gsid_id'] = gs_id

    # داده‌های بارنامه
    waybill_data = Waybill.objects.filter(**filters).values('product_id__name').annotate(
        total_quantity=Sum('quantity'),
        total_received=Sum('received_quantity')
    )

    # داده‌های فروش برای محاسبه موجودی
    sales_filters = {}
    if gs_id:
        sales_filters['gs_id'] = gs_id

    sales_by_product = SellGs.objects.filter(**sales_filters).values('product__name').annotate(
        total_sales=Sum('sell')
    )

    inventory_data = {
        'waybills': list(waybill_data),
        'sales': list(sales_by_product)
    }

    return JsonResponse(inventory_data)


@login_required
def get_kpi_data(request):
    """داده‌های شاخص‌های کلیدی عملکرد"""
    days = int(request.GET.get('days', 7))

    # تاریخ‌ها
    end_date = jdatetime.date.today()
    start_date = end_date - timedelta(days=days)

    # محاسبه KPI ها
    total_sales = SellGs.objects.filter(
        tarikh__gte=start_date,
        tarikh__lte=end_date
    ).aggregate(total=Sum('sell'))['total'] or 0

    total_waybills = Waybill.objects.filter(
        exit_date__gte=start_date.togregorian(),
        exit_date__lte=end_date.togregorian()
    ).count()

    total_stations = GsModel.objects.count()

    # میانگین مغایرت
    avg_discrepancy = SellModel.objects.filter(
        tarikh__gte=start_date,
        tarikh__lte=end_date
    ).aggregate(avg=Avg('ekhtelaf'))['avg'] or 0

    kpi_data = {
        'total_sales': f"{total_sales:,.0f}",
        'total_waybills': total_waybills,
        'active_stations': total_stations,
        'avg_discrepancy': f"{avg_discrepancy:.2f}",
        'sales_trend': 'up',  # می‌توانید منطق ترند را اضافه کنید
        'period': f"{days} روز گذشته"
    }

    return JsonResponse(kpi_data)


@login_required
def get_station_ranking(request):
    """رتبه‌بندی جایگاه‌ها"""
    days = int(request.GET.get('days', 30))

    end_date = jdatetime.date.today()
    start_date = end_date - timedelta(days=days)

    ranking = SellGs.objects.filter(
        tarikh__gte=start_date,
        tarikh__lte=end_date
    ).values('gs__name').annotate(
        total_sales=Sum('sell'),
        total_discrepancy=Sum('ekhtelaf')
    ).order_by('-total_sales')[:10]

    return JsonResponse({'ranking': list(ranking)})


@login_required
def get_waybill_chart_data(request):
    """داده‌های نمودار بارنامه‌های ارسال شده"""
    # دریافت پارامترهای فیلتر
    period = request.GET.get('period', '30d')
    zone_id = request.GET.get('zone_id')
    area_id = request.GET.get('area_id')
    gs_id = request.GET.get('gs_id')
    product_id = request.GET.get('product_id')

    # محاسبه تاریخ‌ها بر اساس دوره
    end_date = jdatetime.date.today()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
        group_by = 'day'
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
        group_by = 'day'
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
        group_by = 'week'
    else:  # 1y
        start_date = end_date - timedelta(days=365)
        group_by = 'month'

    # ساخت فیلترها
    filters = Q(exit_date__gte=start_date.togregorian(),
                exit_date__lte=end_date.togregorian())

    if zone_id != '0':
        filters &= Q(gsid__area__zone_id=zone_id)
    if area_id != '0':
        filters &= Q(gsid__area_id=area_id)
    if gs_id != '0':
        filters &= Q(gsid_id=gs_id)
    if product_id != '0':
        filters &= Q(product_id__product_id=product_id)

    # داده‌های بارنامه
    waybill_data = Waybill.objects.filter(filters).extra(
        select={'period': f"DATE(exit_date)"}
    ).values('period', 'product_id__product_id__name').annotate(
        total_quantity=Sum('quantity'),
        count=Count('id')
    ).order_by('period', 'product_id__product_id__name')

    # فرمت‌دهی داده برای نمودار
    products = list(set([item['product_id__product_id__name'] for item in waybill_data]))
    periods = sorted(list(set([item['period'] for item in waybill_data])))

    datasets = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']

    for i, product in enumerate(products):
        product_data = []
        for period in periods:
            item = next((x for x in waybill_data if x['product_id__product_id__name'] == product and x['period'] == period), None)
            product_data.append(float(item['total_quantity']) if item else 0)

        datasets.append({
            'label': product,
            'data': product_data,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)],
            'borderWidth': 1
        })

    chart_data = {
        'labels': [str(p) for p in periods],
        'datasets': datasets
    }

    return JsonResponse(chart_data)


@login_required
def get_sales_chart_data(request):
    """داده‌های نمودار فروش به تفکیک فرآورده"""
    period = request.GET.get('period', '30d')
    zone_id = request.GET.get('zone_id')
    area_id = request.GET.get('area_id')
    gs_id = request.GET.get('gs_id')
    product_id = request.GET.get('product_id')

    # محاسبه تاریخ‌ها
    end_date = jdatetime.date.today()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    else:  # 1y
        start_date = end_date - timedelta(days=365)

    # ساخت فیلترها
    filters = Q(tarikh__gte=start_date, tarikh__lte=end_date)
    if zone_id != '0':
        filters &= Q(gs__area__zone_id=zone_id)
    if area_id != '0':
        filters &= Q(gs__area_id=area_id)
    if gs_id != '0':
        filters &= Q(gs_id=gs_id)
    if product_id  != '0':
        filters &= Q(product_id=product_id)

    print(filters)

    # داده‌های فروش
    sales_data = SellGs.objects.filter(filters).values(
        'tarikh', 'product__name'
    ).annotate(
        total_sell=Sum('sell'),
        total_yaranee=Sum('yarane'),
        total_azad=Sum('azad')
    ).order_by('tarikh', 'product__name')

    # فرمت‌دهی داده
    products = list(set([item['product__name'] for item in sales_data]))
    dates = sorted(list(set([item['tarikh'] for item in sales_data])))

    datasets = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']

    for i, product in enumerate(products):
        product_data = []
        for date in dates:
            item = next((x for x in sales_data if x['product__name'] == product and x['tarikh'] == date), None)
            product_data.append(float(item['total_sell']) if item else 0)

        datasets.append({
            'label': f'فروش {product}',
            'data': product_data,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',
            'fill': True,
            'tension': 0.4
        })

    chart_data = {
        'labels': [date.strftime('%Y/%m/%d') for date in dates],
        'datasets': datasets
    }

    return JsonResponse(chart_data)


@login_required
def get_inventory_chart_data(request):
    """داده‌های نمودار موجودی مخازن"""
    zone_id = request.GET.get('zone_id')
    area_id = request.GET.get('area_id')
    gs_id = request.GET.get('gs_id')

    # آخرین تاریخ موجود برای هر جایگاه
    latest_dates = Mojodi.objects.values('gs_id').annotate(
        latest_date=Max('tarikh')
    )

    # ساخت فیلترها
    filters = Q()
    if zone_id != '0':
        filters &= Q(gs__area__zone_id=zone_id)
    if area_id != '0':
        filters &= Q(gs__area_id=area_id)
    if gs_id != '0':
        filters &= Q(gs_id=gs_id)

    # داده‌های موجودی
    inventory_data = []
    for latest in latest_dates:
        mojodi = Mojodi.objects.filter(
            gs_id=latest['gs_id'],
            tarikh=latest['latest_date']
        ).filter(filters).first()

        if mojodi:
            inventory_data.append({
                'station': mojodi.gs.name,
                'benzin': mojodi.benzin,
                'super': mojodi.super,
                'gaz': mojodi.gaz,
                'darsad_benzin': mojodi.darsadbenzin(),
                'darsad_super': mojodi.darsadsuper(),
                'darsad_gaz': mojodi.darsadgaz()
            })

    # اگر فیلتر خاصی زده شده، داده‌های تجمیعی
    if zone_id or area_id:
        aggregated_data = Mojodi.objects.filter(
            tarikh__in=[item['latest_date'] for item in latest_dates]
        ).filter(filters).aggregate(
            total_benzin=Sum('benzin'),
            total_super=Sum('super'),
            total_gaz=Sum('gaz')
        )

        chart_data = {
            'type': 'aggregated',
            'labels': ['بنزین', 'سوپر', 'گاز'],
            'datasets': [{
                'label': 'موجودی کل (لیتر)',
                'data': [
                    float(aggregated_data['total_benzin'] or 0),
                    float(aggregated_data['total_super'] or 0),
                    float(aggregated_data['total_gaz'] or 0)
                ],
                'backgroundColor': ['#4e73df', '#1cc88a', '#36b9cc']
            }]
        }
    else:
        # داده‌های تفکیک شده برای جایگاه‌ها
        stations = [item['station'] for item in inventory_data]
        benzin_data = [item['benzin'] for item in inventory_data]
        super_data = [item['super'] for item in inventory_data]
        gaz_data = [item['gaz'] for item in inventory_data]

        chart_data = {
            'type': 'detailed',
            'labels': stations,
            'datasets': [
                {
                    'label': 'بنزین',
                    'data': benzin_data,
                    'backgroundColor': '#4e73df'
                },
                {
                    'label': 'سوپر',
                    'data': super_data,
                    'backgroundColor': '#1cc88a'
                },
                {
                    'label': 'گاز',
                    'data': gaz_data,
                    'backgroundColor': '#36b9cc'
                }
            ]
        }

    return JsonResponse(chart_data)


@login_required
def get_filter_options(request):
    """گزینه‌های فیلتر برای frontend"""
    zones = list(Zone.objects.values('id', 'name'))
    areas = list(GsModel.objects.values('area').distinct())
    products = list(Product.objects.values('id', 'name'))

    return JsonResponse({
        'zones': zones,
        'areas': areas,
        'products': products
    })


@cache_permission('gs')
def gs_map_view(request):
    """نمایش تمام جایگاه‌ها روی نقشه ایران"""
    add_to_log(request, 'مشاهده نقشه جایگاه‌ها', 0)

    # دریافت جایگاه‌ها بر اساس دسترسی کاربر
    gs_list = GsModel.object_role.c_gsmodel(request).filter(
        location__isnull=False
    ).exclude(location='').values(
        'id', 'name', 'gsid', 'location', 'area__name', 'area__zone__name', 'status__name'
    )

    # تبدیل داده‌ها به فرمت مناسب برای JSON
    gs_data = []
    for gs in gs_list:
        try:
            if gs['location'] and ',' in gs['location']:
                lat, lng = gs['location'].split(',')
                gs_data.append({
                    'id': gs['id'],
                    'name': gs['name'],
                    'gsid': gs['gsid'],
                    'lat': float(lat.strip()),
                    'lng': float(lng.strip()),
                    'area': gs['area__name'],
                    'zone': gs['area__zone__name'],
                    'status': gs['status__name'],
                    'encrypted_id': to_md5(str(gs['id']))  # اگر فانکشن to_md5 دارید
                })
        except (ValueError, IndexError):
            continue

    context = {
        'gs_data': gs_data,
        'total_gs': len(gs_data),
        'zones': Zone.objects_limit.all() if request.user.owner.role.role in ['mgr', 'setad'] else None
    }

    return TemplateResponse(request, 'gs_map.html', context)