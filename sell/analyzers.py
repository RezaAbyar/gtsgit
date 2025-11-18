# analyzers.py
import jdatetime
from django.db.models import Sum, Avg, Count, F, Q
from django.utils import timezone
from datetime import timedelta
import statistics

from base.models import Pump
from sell.models import ConsumptionPolicy, SellModel


class PolicyAnalyzer:
    def __init__(self, policy_id=None):
        if policy_id:
            self.policy = ConsumptionPolicy.objects.get(id=policy_id)
        else:
            self.policy = None

    def set_policy(self, policy_id):
        self.policy = ConsumptionPolicy.objects.get(id=policy_id)

    def analyze_policy_impact(self, comparison_days=30):
        """تحلیل کلی تأثیر سیاست"""
        if not self.policy:
            return {"error": "هیچ سیاستی انتخاب نشده است"}

        # دوره‌های مقایسه
        before_period = self._get_period_before_policy(comparison_days)
        after_period = self._get_policy_period()

        # فیلترهای پایه
        base_filters = self._get_base_filters()

        # تحلیل‌های مختلف
        analysis = {
            'policy_info': self._get_policy_info(),
            'sales_impact': self._analyze_sales_impact(before_period, after_period, base_filters),
            'consumption_pattern': self._analyze_consumption_pattern_change(before_period, after_period, base_filters),
            'regional_analysis': self._analyze_regional_impact(before_period, after_period),
            'anomalies': self._detect_anomalies(before_period, after_period, base_filters),
            'time_analysis': self._analyze_time_patterns(before_period, after_period, base_filters)
        }

        return analysis

    def _get_base_filters(self):
        """فیلترهای پایه بر اساس سیاست"""
        filters = {}

        # فیلتر مناطق
        if self.policy.zones.exists():
            filters['gs__area__zone__in'] = self.policy.zones.all()

        # فیلتر محصولات
        if self.policy.products.exists():
            filters['product__in'] = self.policy.products.all()

        return filters

    def _get_period_before_policy(self, days=30):
        """دوره قبل از اجرای سیاست"""
        start_before = self.policy.start_date - timedelta(days=days)
        end_before = self.policy.start_date - timedelta(days=1)

        return {
            'start': start_before,
            'end': end_before,
            'label': f'{days} روز قبل از سیاست'
        }

    def _get_policy_period(self):
        """دوره اجرای سیاست"""
        end_date = self.policy.end_date if self.policy.end_date else timezone.now().date()

        return {
            'start': self.policy.start_date,
            'end': end_date,
            'label': 'دوره اجرای سیاست'
        }

    # analyzers.py - ادامه
    def _analyze_consumption_pattern_change(self, before_period, after_period, base_filters):
        """تحلیل تغییر الگوی مصرف"""

        # ۱. میانگین حجم هر تراکنش
        avg_transaction_before = SellModel.objects.filter(
            tarikh__range=[before_period['start'], before_period['end']],
            **base_filters
        ).aggregate(avg_sell=Avg('sell'))['avg_sell'] or 0

        avg_transaction_after = SellModel.objects.filter(
            tarikh__range=[after_period['start'], after_period['end']],
            **base_filters
        ).aggregate(avg_sell=Avg('sell'))['avg_sell'] or 0

        # ۲. توزیع فروش بین نازل‌ها
        nozzle_distribution_before = self._get_nozzle_distribution(before_period, base_filters)
        nozzle_distribution_after = self._get_nozzle_distribution(after_period, base_filters)

        # ۳. تغییرات در ساعات پیک مصرف
        hourly_pattern_before = self._get_hourly_pattern(before_period, base_filters)
        hourly_pattern_after = self._get_hourly_pattern(after_period, base_filters)

        return {
            'avg_transaction_size': {
                'before': round(avg_transaction_before, 2),
                'after': round(avg_transaction_after, 2),
                'change_percent': self._calculate_percent_change(avg_transaction_before, avg_transaction_after)
            },
            'nozzle_distribution_change': self._compare_nozzle_distribution(
                nozzle_distribution_before,
                nozzle_distribution_after
            ),
            'hourly_pattern_change': self._compare_hourly_patterns(
                hourly_pattern_before,
                hourly_pattern_after
            )
        }

    def _get_nozzle_distribution(self, period, filters):
        """توزیع فروش بین نازل‌ها"""
        distribution = SellModel.objects.filter(
            tarikh__range=[period['start'], period['end']],
            **filters
        ).values('tolombeinfo__name', 'pumpnumber').annotate(
            total_sales=Sum('sell'),
            transaction_count=Count('id')
        ).order_by('-total_sales')

        return list(distribution)

    def _get_hourly_pattern(self, period, filters):
        """الگوی ساعتی مصرف (با استفاده از create field)"""
        # اگر فیلد ساعت دارید، ازش استفاده کنید. در غیر این صورت از create
        hourly_data = SellModel.objects.filter(
            tarikh__range=[period['start'], period['end']],
            **filters
        ).extra({
            'hour': "EXTRACT(hour FROM create)"
        }).values('hour').annotate(
            total_sales=Sum('sell'),
            transaction_count=Count('id')
        ).order_by('hour')

        return list(hourly_data)

    # analyzers.py - ادامه
    def _detect_anomalies(self, before_period, after_period, base_filters):
        """شناسایی رفتارهای غیرعادی"""

        anomalies = {
            'unusual_gs_changes': [],
            'nozzle_behavior_changes': [],
            'regional_outliers': []
        }

        # ۱. جایگاه‌هایی با بیشترین تغییر
        gs_changes = self._get_gs_with_most_change(before_period, after_period, base_filters)
        anomalies['unusual_gs_changes'] = gs_changes[:10]  # 10 تا اول

        # ۲. نازل‌هایی که الگوی مصرفشون تغییر کرد
        nozzle_changes = self._get_nozzle_behavior_changes(before_period, after_period, base_filters)
        anomalies['nozzle_behavior_changes'] = nozzle_changes[:10]

        # ۳. مناطق با بیشترین/کمترین تأثیرپذیری
        regional_impact = self._get_regional_impact_outliers(before_period, after_period)
        anomalies['regional_outliers'] = regional_impact

        return anomalies

    def _get_gs_with_most_change(self, before_period, after_period, filters):
        """جایگاه‌هایی با بیشترین تغییر در فروش"""

        # محاسبه فروش قبل برای هر جایگاه
        gs_sales_before = {}
        before_sales = SellModel.objects.filter(
            tarikh__range=[before_period['start'], before_period['end']],
            **filters
        ).values('gs_id', 'gs__name').annotate(
            total_sales=Sum('sell')
        )

        for item in before_sales:
            gs_sales_before[item['gs_id']] = item['total_sales']

        # محاسبه فروش بعد برای هر جایگاه
        gs_changes = []
        after_sales = SellModel.objects.filter(
            tarikh__range=[after_period['start'], after_period['end']],
            **filters
        ).values('gs_id', 'gs__name').annotate(
            total_sales=Sum('sell')
        )

        for item in after_sales:
            gs_id = item['gs_id']
            sales_after = item['total_sales']
            sales_before = gs_sales_before.get(gs_id, 0)

            if sales_before > 0:  # جلوگیری از تقسیم بر صفر
                change_percent = ((sales_after - sales_before) / sales_before) * 100

                gs_changes.append({
                    'gs_id': gs_id,
                    'gs_name': item['gs__name'],
                    'sales_before': sales_before,
                    'sales_after': sales_after,
                    'change_percent': round(change_percent, 2),
                    'change_type': 'کاهش' if change_percent < 0 else 'افزایش'
                })

        # مرتب‌سازی بر اساس میزان تغییر
        return sorted(gs_changes, key=lambda x: abs(x['change_percent']), reverse=True)

    def _get_nozzle_behavior_changes(self, before_period, after_period, filters):
        """تغییرات رفتار نازل‌ها"""

        nozzle_changes = []

        # گرفتن داده‌های تمام نازل‌ها
        all_nozzles = Pump.objects.filter(
            **{k.replace('gs__area', 'gs__area') if 'gs__area' in k else k: v
               for k, v in filters.items()}
        ).distinct()

        for nozzle in all_nozzles:
            # فروش قبل
            sales_before = SellModel.objects.filter(
                tolombeinfo=nozzle,
                tarikh__range=[before_period['start'], before_period['end']]
            ).aggregate(total=Sum('sell'))['total'] or 0

            # فروش بعد
            sales_after = SellModel.objects.filter(
                tolombeinfo=nozzle,
                tarikh__range=[after_period['start'], after_period['end']]
            ).aggregate(total=Sum('sell'))['total'] or 0

            if sales_before > 0:
                change_percent = ((sales_after - sales_before) / sales_before) * 100

                # فقط تغییرات قابل توجه
                if abs(change_percent) > 10:  # بیشتر از ۱۰٪ تغییر
                    nozzle_changes.append({
                        'nozzle_id': nozzle.id,
                        'nozzle_name': nozzle.name,
                        'gs_name': nozzle.gs.name,
                        'sales_before': sales_before,
                        'sales_after': sales_after,
                        'change_percent': round(change_percent, 2)
                    })

        return sorted(nozzle_changes, key=lambda x: abs(x['change_percent']), reverse=True)

    # analyzers.py - اضافه کردن به کلاس PolicyAnalyzer
    def get_daily_comparison_data(self, comparison_days=30):
        """گرفتن داده‌های روزانه برای نمودار مقایسه‌ای"""

        before_period = self._get_period_before_policy(comparison_days)
        after_period = self._get_policy_period()
        base_filters = self._get_base_filters()

        daily_data = {
            'labels': [],
            'before_data': [],
            'after_data': [],
            'policy_info': self._get_policy_info()
        }

        # داده‌های روزانه برای دوره قبل
        before_daily = SellModel.objects.filter(
            tarikh__range=[before_period['start'], before_period['end']],
            **base_filters
        ).values('tarikh').annotate(
            daily_sales=Sum('sell'),
            daily_transactions=Count('id')
        ).order_by('tarikh')

        # داده‌های روزانه برای دوره بعد
        after_daily = SellModel.objects.filter(
            tarikh__range=[after_period['start'], after_period['end']],
            **base_filters
        ).values('tarikh').annotate(
            daily_sales=Sum('sell'),
            daily_transactions=Count('id')
        ).order_by('tarikh')

        # ایجاد لیبل‌های تاریخ
        all_dates = set()

        # اضافه کردن تاریخ‌های دوره قبل
        for item in before_daily:
            date_str = item['tarikh'].strftime('%Y-%m-%d')
            all_dates.add(date_str)
            daily_data['before_data'].append({
                'date': date_str,
                'sales': float(item['daily_sales'] or 0),
                'transactions': item['daily_transactions']
            })

        # اضافه کردن تاریخ‌های دوره بعد
        for item in after_daily:
            date_str = item['tarikh'].strftime('%Y-%m-%d')
            all_dates.add(date_str)
            daily_data['after_data'].append({
                'date': date_str,
                'sales': float(item['daily_sales'] or 0),
                'transactions': item['daily_transactions']
            })

        # مرتب‌سازی تاریخ‌ها
        daily_data['labels'] = sorted(list(all_dates))

        return daily_data

    def _get_policy_info(self):
        """اطلاعات سیاست برای نمایش"""
        return {
            'id': self.policy.id,
            'name': self.policy.name,
            'type': self.policy.get_policy_type_display(),
            'start_date': self.policy.start_date.strftime('%Y-%m-%d'),
            'end_date': self.policy.end_date.strftime('%Y-%m-%d') if self.policy.end_date else 'نامشخص',
            'daily_limit': self.policy.daily_limit,
            'zones_count': self.policy.zones.count(),
            'products': [product.name for product in self.policy.products.all()],
            'is_active': self.policy.is_currently_active()
        }

    def _analyze_sales_impact(self, before_period, after_period, base_filters):
        """تحلیل تأثیر بر فروش"""

        # آمار دوره قبل
        stats_before = SellModel.objects.filter(
            tarikh__range=[before_period['start'], before_period['end']],
            **base_filters
        ).aggregate(
            total_sales=Sum('sell') or 0,
            total_transactions=Count('id'),
            avg_sales=Avg('sell') or 0,
            unique_gs=Count('gs', distinct=True)
        )

        # آمار دوره بعد
        stats_after = SellModel.objects.filter(
            tarikh__range=[after_period['start'], after_period['end']],
            **base_filters
        ).aggregate(
            total_sales=Sum('sell') or 0,
            total_transactions=Count('id'),
            avg_sales=Avg('sell') or 0,
            unique_gs=Count('gs', distinct=True)
        )

        # محاسبه درصد تغییرات
        total_change = self._calculate_percent_change(stats_before['total_sales'], stats_after['total_sales'])
        transaction_change = self._calculate_percent_change(stats_before['total_transactions'],
                                                            stats_after['total_transactions'])
        avg_transaction_change = self._calculate_percent_change(stats_before['avg_sales'], stats_after['avg_sales'])

        return {
            'total_sales_before': stats_before['total_sales'],
            'total_sales_after': stats_after['total_sales'],
            'total_change': round(total_change, 2),
            'transaction_count_before': stats_before['total_transactions'],
            'transaction_count_after': stats_after['total_transactions'],
            'transaction_change': round(transaction_change, 2),
            'avg_transaction_before': round(stats_before['avg_sales'], 2),
            'avg_transaction_after': round(stats_after['avg_sales'], 2),
            'avg_transaction_change': round(avg_transaction_change, 2),
            'gs_count_before': stats_before['unique_gs'],
            'gs_count_after': stats_after['unique_gs']
        }

    def _calculate_percent_change(self, before, after):
        """محاسبه درصد تغییر"""
        if before == 0 or not before:
            after=0
            return 100.0 if after > 0 else 0.0
        return ((after - before) / before) * 100