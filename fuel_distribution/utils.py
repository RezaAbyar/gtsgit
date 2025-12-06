from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from .models import (
    SuperFuelImport, ImportToDistributor, DistributionToGasStation,
    FuelStock, UserDistributionProfile
)
from base.models import Owner, Company, GsModel


# ============================
# توابع کمکی گزارش‌گیری
# ============================

def generate_import_report(user, period_start, period_end, company=None):
    """
    تولید گزارش واردات
    """
    # فیلتر بر اساس کاربر و تاریخ
    queryset = SuperFuelImport.objects.filter(
        importer=user,
        import_date__range=[period_start, period_end]
    )

    # اگر شرکت مشخص شده
    if company:
        queryset = queryset.filter(company=company)

    # جمع‌آوری آمار
    stats = {
        'total_imports': queryset.count(),
        'total_liters': queryset.aggregate(total=Sum('amount_liters'))['total'] or 0,
        'pending_count': queryset.filter(status='pending').count(),
        'confirmed_count': queryset.filter(status='confirmed').count(),
        'distributed_count': queryset.filter(status='distributed').count(),
        'cancelled_count': queryset.filter(status='cancelled').count(),
    }

    # جزئیات هر واردات
    import_details = list(queryset.values(
        'import_date', 'amount_liters', 'tracking_number',
        'status', 'created_at'
    ).order_by('-import_date'))

    # توزیع‌های انجام شده
    distributions = ImportToDistributor.objects.filter(
        fuel_import__in=queryset
    ).values(
        'distribution_date', 'distributor__name', 'distributor__lname',
        'amount_liters', 'price_per_liter'
    ).order_by('-distribution_date')

    report_data = {
        'report_type': 'imports',
        'period_start': period_start.strftime('%Y/%m/%d'),
        'period_end': period_end.strftime('%Y/%m/%d'),
        'company': company.name if company else 'همه شرکت‌ها',
        'generated_at': timezone.now().strftime('%Y/%m/%d %H:%M'),
        'stats': stats,
        'imports': import_details,
        'distributions': list(distributions),
    }

    return report_data


def generate_distribution_report(user, period_start, period_end, company=None):
    """
    تولید گزارش توزیع
    """
    # تشخیص نقش کاربر
    try:
        profile = user.distribution_profile
    except UserDistributionProfile.DoesNotExist:
        return {'error': 'پروفایل توزیع یافت نشد'}

    report_data = {
        'report_type': 'distributions',
        'period_start': period_start.strftime('%Y/%m/%d'),
        'period_end': period_end.strftime('%Y/%m/%d'),
        'company': company.name if company else 'همه شرکت‌ها',
        'generated_at': timezone.now().strftime('%Y/%m/%d %H:%M'),
        'user_role': profile.role,
        'user_company': profile.company.name,
    }

    if profile.role == 'importer':
        # گزارش برای واردکننده
        distributions = ImportToDistributor.objects.filter(
            fuel_import__importer=user,
            distribution_date__range=[period_start, period_end]
        )

        if company:
            distributions = distributions.filter(distributor_company=company)

        stats = {
            'total_distributions': distributions.count(),
            'total_liters': distributions.aggregate(total=Sum('amount_liters'))['total'] or 0,
            'avg_price': distributions.aggregate(avg=Avg('price_per_liter'))['avg'] or 0,
        }

        # توزیع بر اساس توزیع‌کننده
        by_distributor = distributions.values(
            'distributor__name', 'distributor__lname', 'distributor_company__name'
        ).annotate(
            total_liters=Sum('amount_liters'),
            total_price=Sum('amount_liters') * Avg('price_per_liter'),
            count=Count('id')
        ).order_by('-total_liters')

        report_data.update({
            'stats': stats,
            'by_distributor': list(by_distributor),
            'distributions': list(distributions.values(
                'distribution_date', 'distributor__name', 'distributor__lname',
                'amount_liters', 'price_per_liter', 'document_number'
            ).order_by('-distribution_date')),
        })

    elif profile.role == 'distributor':
        # گزارش برای توزیع‌کننده
        # دریافت از واردکننده
        received = ImportToDistributor.objects.filter(
            distributor=user,
            distribution_date__range=[period_start, period_end]
        )

        # تحویل به جایگاه‌ها
        deliveries = DistributionToGasStation.objects.filter(
            distributor_gas_station__distributor=user,
            delivery_date__range=[period_start, period_end]
        )

        stats = {
            'total_received': received.aggregate(total=Sum('amount_liters'))['total'] or 0,
            'total_delivered': deliveries.aggregate(total=Sum('amount_liters'))['total'] or 0,
            'remaining_stock': (received.aggregate(total=Sum('amount_liters'))['total'] or 0) -
                               (deliveries.aggregate(total=Sum('amount_liters'))['total'] or 0),
            'delivery_count': deliveries.count(),
        }

        # تحویل بر اساس جایگاه
        by_station = deliveries.values(
            'distributor_gas_station__gas_station__name',
            'distributor_gas_station__gas_station__gsid'
        ).annotate(
            total_liters=Sum('amount_liters'),
            avg_price=Avg('price_per_liter'),
            count=Count('id')
        ).order_by('-total_liters')

        report_data.update({
            'stats': stats,
            'by_station': list(by_station),
            'received': list(received.values(
                'distribution_date', 'fuel_import__importer__name',
                'fuel_import__importer__lname', 'amount_liters',
                'price_per_liter'
            ).order_by('-distribution_date')),
            'deliveries': list(deliveries.values(
                'delivery_date', 'distributor_gas_station__gas_station__name',
                'amount_liters', 'price_per_liter', 'status'
            ).order_by('-delivery_date')),
        })

    return report_data


def generate_stock_report(user, period_start, period_end, company=None):
    """
    تولید گزارش موجودی
    """
    try:
        profile = user.distribution_profile
    except UserDistributionProfile.DoesNotExist:
        return {'error': 'پروفایل توزیع یافت نشد'}

    report_data = {
        'report_type': 'stock',
        'period_start': period_start.strftime('%Y/%m/%d'),
        'period_end': period_end.strftime('%Y/%m/%d'),
        'generated_at': timezone.now().strftime('%Y/%m/%d %H:%M'),
        'user_role': profile.role,
        'user_company': profile.company.name,
    }

    if profile.role == 'importer':
        # موجودی واردکننده
        imports = SuperFuelImport.objects.filter(
            importer=user,
            import_date__range=[period_start, period_end],
            status__in=['confirmed', 'distributed']
        )

        distributions = ImportToDistributor.objects.filter(
            fuel_import__importer=user,
            distribution_date__range=[period_start, period_end]
        )

        # محاسبه موجودی روزانه
        stock_history = []
        current_date = period_start
        cumulative_import = 0
        cumulative_distribution = 0

        while current_date <= period_end:
            daily_import = imports.filter(
                import_date__date=current_date
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            daily_distribution = distributions.filter(
                distribution_date__date=current_date
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            cumulative_import += daily_import
            cumulative_distribution += daily_distribution
            daily_stock = cumulative_import - cumulative_distribution

            stock_history.append({
                'date': current_date.strftime('%Y/%m/%d'),
                'import': daily_import,
                'distribution': daily_distribution,
                'stock': daily_stock,
                'cumulative_import': cumulative_import,
                'cumulative_distribution': cumulative_distribution,
            })

            current_date += timedelta(days=1)

        report_data.update({
            'total_import': cumulative_import,
            'total_distribution': cumulative_distribution,
            'current_stock': cumulative_import - cumulative_distribution,
            'stock_history': stock_history,
            'daily_avg_import': cumulative_import / len(stock_history) if stock_history else 0,
            'daily_avg_distribution': cumulative_distribution / len(stock_history) if stock_history else 0,
        })

    elif profile.role == 'distributor':
        # موجودی توزیع‌کننده
        received = ImportToDistributor.objects.filter(
            distributor=user,
            distribution_date__range=[period_start, period_end]
        )

        deliveries = DistributionToGasStation.objects.filter(
            distributor_gas_station__distributor=user,
            delivery_date__range=[period_start, period_end]
        )

        # محاسبه موجودی روزانه
        stock_history = []
        current_date = period_start
        cumulative_received = 0
        cumulative_delivered = 0

        while current_date <= period_end:
            daily_received = received.filter(
                distribution_date__date=current_date
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            daily_delivered = deliveries.filter(
                delivery_date__date=current_date
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            cumulative_received += daily_received
            cumulative_delivered += daily_delivered
            daily_stock = cumulative_received - cumulative_delivered

            stock_history.append({
                'date': current_date.strftime('%Y/%m/%d'),
                'received': daily_received,
                'delivered': daily_delivered,
                'stock': daily_stock,
                'cumulative_received': cumulative_received,
                'cumulative_delivered': cumulative_delivered,
            })

            current_date += timedelta(days=1)

        # موجودی هر جایگاه
        station_stock = []
        deliveries_by_station = deliveries.values(
            'distributor_gas_station__gas_station__name',
            'distributor_gas_station__gas_station__gsid'
        ).annotate(
            total_delivered=Sum('amount_liters')
        )

        for station in deliveries_by_station:
            station_stock.append({
                'station_name': station['distributor_gas_station__gas_station__name'],
                'station_id': station['distributor_gas_station__gas_station__gsid'],
                'total_delivered': station['total_delivered'],
            })

        report_data.update({
            'total_received': cumulative_received,
            'total_delivered': cumulative_delivered,
            'current_stock': cumulative_received - cumulative_delivered,
            'stock_history': stock_history,
            'station_stock': station_stock,
            'daily_avg_received': cumulative_received / len(stock_history) if stock_history else 0,
            'daily_avg_delivered': cumulative_delivered / len(stock_history) if stock_history else 0,
        })

    return report_data


def check_user_distribution_role(user, required_role):
    """
    بررسی نقش کاربر در سیستم توزیع
    """
    try:
        profile = user.distribution_profile
        return profile.role == required_role
    except UserDistributionProfile.DoesNotExist:
        return False


def calculate_distribution_chain(import_id):
    """
    محاسبه زنجیره توزیع یک ورود خاص
    """
    try:
        import_record = SuperFuelImport.objects.get(id=import_id)

        # توزیع‌های انجام شده از این ورود
        distributions = ImportToDistributor.objects.filter(
            fuel_import=import_record
        )

        chain_data = {
            'import': {
                'id': import_record.id,
                'date': import_record.import_date,
                'amount': import_record.amount_liters,
                'tracking_number': import_record.tracking_number,
            },
            'distributions': [],
            'total_distributed': distributions.aggregate(total=Sum('amount_liters'))['total'] or 0,
            'remaining': import_record.remaining_amount,
        }

        for dist in distributions:
            # تحویل‌های هر توزیع
            deliveries = DistributionToGasStation.objects.filter(
                distributor_distribution=dist
            )

            distributor_data = {
                'distributor': {
                    'name': dist.distributor.get_full_name(),
                    'company': dist.distributor_company.name,
                },
                'distribution_date': dist.distribution_date,
                'amount': dist.amount_liters,
                'price': dist.price_per_liter,
                'deliveries': []
            }

            for delivery in deliveries:
                delivery_data = {
                    'gas_station': delivery.distributor_gas_station.gas_station.name,
                    'gsid': delivery.distributor_gas_station.gas_station.gsid,
                    'delivery_date': delivery.delivery_date,
                    'amount': delivery.amount_liters,
                    'price': delivery.price_per_liter,
                    'status': delivery.get_status_display(),
                }
                distributor_data['deliveries'].append(delivery_data)

            chain_data['distributions'].append(distributor_data)

        return chain_data

    except SuperFuelImport.DoesNotExist:
        return {'error': 'ورود یافت نشد'}


def get_stock_alerts(user, threshold_percent=20):
    """
    دریافت هشدارهای موجودی پایین
    """
    try:
        profile = user.distribution_profile
        alerts = []

        if profile.role == 'distributor':
            stock = FuelStock.objects.filter(company=profile.company).first()

            if stock:
                # محاسبه درصد موجودی باقی‌مانده
                if stock.total_imported > 0:
                    remaining_percent = (stock.current_stock / stock.total_imported) * 100

                    if remaining_percent < threshold_percent:
                        alerts.append({
                            'type': 'low_stock',
                            'message': f'موجودی شما به {remaining_percent:.1f}% رسیده است',
                            'severity': 'warning' if remaining_percent > 10 else 'danger',
                            'current_stock': stock.current_stock,
                            'remaining_percent': remaining_percent,
                        })

                # هشدار برای توزیع‌های در انتظار
                pending_deliveries = DistributionToGasStation.objects.filter(
                    distributor_gas_station__distributor=user,
                    status='scheduled'
                ).count()

                if pending_deliveries > 0:
                    alerts.append({
                        'type': 'pending_deliveries',
                        'message': f'{pending_deliveries} تحویل در انتظار دارید',
                        'severity': 'info',
                        'count': pending_deliveries,
                    })

        elif profile.role == 'importer':
            # هشدار برای واردات در انتظار تأیید
            pending_imports = SuperFuelImport.objects.filter(
                importer=user,
                status='pending'
            ).count()

            if pending_imports > 0:
                alerts.append({
                    'type': 'pending_imports',
                    'message': f'{pending_imports} واردات در انتظار تأیید دارید',
                    'severity': 'warning',
                    'count': pending_imports,
                })

            # هشدار برای ورودی‌هایی که مقدار زیادی باقی‌مانده دارند
            imports_with_stock = SuperFuelImport.objects.filter(
                importer=user,
                status='confirmed'
            ).exclude(remaining_amount=0)

            for imp in imports_with_stock:
                if imp.remaining_amount > 10000:  # 10,000 لیتر
                    alerts.append({
                        'type': 'high_remaining',
                        'message': f'ورودی {imp.tracking_number} مقدار زیادی باقی‌مانده دارد',
                        'severity': 'info',
                        'tracking_number': imp.tracking_number,
                        'remaining_amount': imp.remaining_amount,
                    })

        return alerts

    except UserDistributionProfile.DoesNotExist:
        return []


def calculate_financial_summary(user, start_date, end_date):
    """
    محاسبه خلاصه مالی
    """
    try:
        profile = user.distribution_profile
        summary = {
            'total_value': 0,
            'total_volume': 0,
            'avg_price': 0,
            'transactions': 0,
        }

        if profile.role == 'importer':
            # مالیات و عوارض برای واردکننده
            distributions = ImportToDistributor.objects.filter(
                fuel_import__importer=user,
                distribution_date__range=[start_date, end_date]
            )

            total_value = 0
            total_volume = 0

            for dist in distributions:
                total_value += dist.amount_liters * dist.price_per_liter
                total_volume += dist.amount_liters

            summary.update({
                'total_value': total_value,
                'total_volume': total_volume,
                'avg_price': total_value / total_volume if total_volume > 0 else 0,
                'transactions': distributions.count(),
            })

        elif profile.role == 'distributor':
            # مالیات و عوارض برای توزیع‌کننده
            # درآمد از فروش به جایگاه‌ها
            deliveries = DistributionToGasStation.objects.filter(
                distributor_gas_station__distributor=user,
                delivery_date__range=[start_date, end_date],
                status='delivered'
            )

            # هزینه از خرید از واردکننده
            received = ImportToDistributor.objects.filter(
                distributor=user,
                distribution_date__range=[start_date, end_date]
            )

            revenue = 0
            cost = 0

            for delivery in deliveries:
                revenue += delivery.amount_liters * delivery.price_per_liter

            for rec in received:
                cost += rec.amount_liters * rec.price_per_liter

            profit = revenue - cost
            profit_margin = (profit / cost * 100) if cost > 0 else 0

            summary.update({
                'revenue': revenue,
                'cost': cost,
                'profit': profit,
                'profit_margin': profit_margin,
                'transactions': deliveries.count() + received.count(),
            })

        return summary

    except UserDistributionProfile.DoesNotExist:
        return {}


def validate_distribution_amount(distribution_id, amount_to_distribute):
    """
    اعتبارسنجی مقدار توزیع
    """
    try:
        distribution = ImportToDistributor.objects.get(id=distribution_id)

        # محاسبه مقدار قبلاً توزیع شده
        already_distributed = DistributionToGasStation.objects.filter(
            distributor_distribution=distribution,
            status__in=['scheduled', 'in_transit', 'delivered']
        ).aggregate(total=Sum('amount_liters'))['total'] or 0

        remaining = distribution.amount_liters - already_distributed

        return {
            'valid': amount_to_distribute <= remaining,
            'remaining': remaining,
            'max_allowed': remaining,
            'message': f'حداکثر مقدار قابل توزیع: {remaining} لیتر' if amount_to_distribute > remaining else 'مقدار معتبر'
        }

    except ImportToDistributor.DoesNotExist:
        return {
            'valid': False,
            'message': 'توزیع یافت نشد'
        }


def export_report_to_excel(report_data, format='xlsx'):
    """
    صادر کردن گزارش به اکسل
    """
    import pandas as pd
    from io import BytesIO
    import tempfile

    try:
        # ایجاد DataFrame بر اساس نوع گزارش
        if report_data['report_type'] == 'imports':
            df = pd.DataFrame(report_data['imports'])
        elif report_data['report_type'] == 'distributions':
            if 'distributions' in report_data:
                df = pd.DataFrame(report_data['distributions'])
            elif 'deliveries' in report_data:
                df = pd.DataFrame(report_data['deliveries'])
            else:
                df = pd.DataFrame()
        elif report_data['report_type'] == 'stock':
            df = pd.DataFrame(report_data['stock_history'])
        else:
            df = pd.DataFrame()

        # ذخیره در فایل موقت
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='گزارش', index=False)

                # اضافه کردن خلاصه
                summary_df = pd.DataFrame([{
                    'نوع گزارش': report_data['report_type'],
                    'دوره': f"{report_data['period_start']} تا {report_data['period_end']}",
                    'تاریخ تولید': report_data['generated_at'],
                    'شرکت': report_data.get('company', ''),
                }])
                summary_df.to_excel(writer, sheet_name='خلاصه', index=False)

            tmp_path = tmp.name

        return tmp_path

    except Exception as e:
        print(f"خطا در تولید اکسل: {e}")
        return None


def send_stock_notification(user, stock_data):
    """
    ارسال اعلان موجودی
    """
    # این تابع می‌تواند برای ارسال ایمیل، پیامک یا نوتیفیکیشن باشد
    notification = {
        'user': user.get_full_name(),
        'type': 'stock_notification',
        'timestamp': timezone.now(),
        'data': stock_data,
    }

    # در اینجا می‌توانید منطق ارسال اعلان را پیاده‌سازی کنید
    # به عنوان مثال:
    # send_email(user.email, 'اعلان موجودی', notification)
    # send_sms(user.mobile, notification)

    return notification


# ============================
# توابع کمکی برای الگوها
# ============================

def get_role_display_name(role_code):
    """
    تبدیل کد نقش به نام فارسی
    """
    role_names = {
        'importer': 'واردکننده',
        'distributor': 'توزیع‌کننده',
        'gas_station': 'جایگاه',
    }
    return role_names.get(role_code, role_code)


def format_iranian_number(number):
    """
    فرمت اعداد به صورت فارسی
    """
    if number is None:
        return '۰'

    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'

    # تبدیل به رشته
    num_str = str(number)

    # جداکننده هزارگان
    parts = []
    while num_str:
        parts.append(num_str[-3:])
        num_str = num_str[:-3]

    formatted = '،'.join(reversed(parts))

    # تبدیل اعداد انگلیسی به فارسی
    for eng, per in zip(english_digits, persian_digits):
        formatted = formatted.replace(eng, per)

    return formatted


def calculate_age(date_value):
    """
    محاسبه سن بر اساس تاریخ
    """
    if not date_value:
        return 0

    today = timezone.now().date()
    age = today.year - date_value.year

    # تنظیم برای ماه و روز
    if (today.month, today.day) < (date_value.month, date_value.day):
        age -= 1

    return age