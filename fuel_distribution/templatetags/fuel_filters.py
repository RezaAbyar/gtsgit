# fuel_distribution/templatetags/fuel_filters.py

from django import template
from django.db.models import QuerySet
import math

register = template.Library()


@register.filter
def sum_amount(queryset, field_name):
    """
    جمع مقادیر یک فیلد از queryset
    """
    if not queryset:
        return 0

    total = 0
    for item in queryset:
        # اگر queryset باشد
        if hasattr(item, field_name):
            value = getattr(item, field_name)
            if value is not None:
                try:
                    total += float(value)
                except (ValueError, TypeError):
                    pass
        # اگر dictionary باشد
        elif isinstance(item, dict) and field_name in item:
            value = item[field_name]
            if value is not None:
                try:
                    total += float(value)
                except (ValueError, TypeError):
                    pass

    return total


@register.filter
def avg_amount(queryset, field_name):
    """
    میانگین مقادیر یک فیلد از queryset
    """
    if not queryset:
        return 0

    total = 0
    count = 0

    for item in queryset:
        if hasattr(item, field_name):
            value = getattr(item, field_name)
            if value is not None:
                try:
                    total += float(value)
                    count += 1
                except (ValueError, TypeError):
                    pass
        elif isinstance(item, dict) and field_name in item:
            value = item[field_name]
            if value is not None:
                try:
                    total += float(value)
                    count += 1
                except (ValueError, TypeError):
                    pass

    return total / count if count > 0 else 0


@register.filter
def multiply(value, arg):
    """
    ضرب دو عدد
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    تقسیم دو عدد
    """
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError):
        return 0


@register.filter
def subtract(value, arg):
    """
    تفریق دو عدد
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def filter_by_status(queryset, status):
    """
    فیلتر کردن بر اساس وضعیت
    """
    if not queryset:
        return []

    filtered = []
    for item in queryset:
        if hasattr(item, 'status'):
            if item.status == status:
                filtered.append(item)
        elif isinstance(item, dict) and 'status' in item:
            if item['status'] == status:
                filtered.append(item)

    return filtered


@register.filter
def get_item(dictionary, key):
    """
    دریافت مقدار از دیکشنری
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


@register.filter
def persian_numbers(value):
    """
    تبدیل اعداد انگلیسی به فارسی
    """
    if value is None:
        return ''

    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'

    value_str = str(value)
    for eng, per in zip(english_digits, persian_digits):
        value_str = value_str.replace(eng, per)

    return value_str


@register.filter
def format_thousands(value):
    """
    فرمت اعداد با جداکننده هزارگان
    """
    if value is None:
        return '۰'

    try:
        # تبدیل به عدد
        num = float(value)

        # فرمت با جداکننده
        if num.is_integer():
            formatted = f"{int(num):,}"
        else:
            formatted = f"{num:,.2f}"

        # تبدیل جداکننده به فارسی
        formatted = formatted.replace(",", "٬")

        # تبدیل اعداد به فارسی
        return persian_numbers(formatted)
    except (ValueError, TypeError):
        return persian_numbers(str(value))


@register.filter
def length(queryset):
    """
    تعداد آیتم‌ها در queryset
    """
    if not queryset:
        return 0

    if isinstance(queryset, QuerySet):
        return queryset.count()
    elif hasattr(queryset, '__len__'):
        return len(queryset)
    return 0


@register.filter
def first_item(queryset):
    """
    اولین آیتم از queryset
    """
    if not queryset:
        return None

    if isinstance(queryset, QuerySet):
        return queryset.first()
    elif hasattr(queryset, '__getitem__'):
        return queryset[0] if queryset else None
    return None


@register.filter
def slice_items(queryset, count):
    """
    برش queryset
    """
    if not queryset:
        return []

    try:
        count = int(count)
        if isinstance(queryset, QuerySet):
            return list(queryset[:count])
        elif hasattr(queryset, '__getitem__'):
            return queryset[:count]
    except (ValueError, TypeError):
        pass

    return queryset


@register.filter(name='filterby')
def filterby_filter(queryset, field_and_value):
    """
    فیلتر کردن بر اساس فیلد و مقدار
    فرمت: "field_name:value"
    مثال: "status:delivered"
    """
    if not queryset:
        return []

    try:
        # جداسازی نام فیلد و مقدار
        if ':' in field_and_value:
            field_name, value = field_and_value.split(':', 1)
        else:
            field_name = field_and_value
            value = None

        filtered = []
        for item in queryset:
            if hasattr(item, field_name):
                field_value = getattr(item, field_name)
                if value is None or str(field_value) == value:
                    filtered.append(item)
            elif isinstance(item, dict) and field_name in item:
                field_value = item[field_name]
                if value is None or str(field_value) == value:
                    filtered.append(item)

        return filtered
    except:
        return queryset


@register.filter
def get_item(dictionary, key):
    """گرفتن آیتم از دیکشنری با کلید"""
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    """ضرب دو عدد"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """تقسیم دو عدد"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0


@register.filter
def average_liters(queryset):
    """میانگین لیتر فروش"""
    try:
        total = sum(sale.sold_liters for sale in queryset)
        return total / len(queryset) if len(queryset) > 0 else 0
    except:
        return 0


@register.filter
def average_amount(queryset):
    """میانگین مبلغ فروش"""
    try:
        total = sum(sale.total_amount for sale in queryset)
        return total / len(queryset) if len(queryset) > 0 else 0
    except:
        return 0


@register.filter
def sum(queryset, field_name):
    """مجموع یک فیلد از کوئری‌ست"""
    try:
        return sum(getattr(item, field_name) for item in queryset)
    except:
        return 0


@register.filter
def average(queryset, field_name=None):
    """میانگین یک فیلد از کوئری‌ست"""
    try:
        if field_name:
            values = [getattr(item, field_name) for item in queryset]
        else:
            values = list(queryset)

        if isinstance(values[0], dict) and 'difference' in values[0]:
            values = [item['difference'] for item in values]

        total = sum(values)
        return total / len(values) if len(values) > 0 else 0
    except:
        return 0


@register.filter
def max_positive_difference(queryset):
    """بیشترین مازاد موجودی"""
    try:
        positive_diffs = [item.difference for item in queryset if item.difference > 0]
        return max(positive_diffs) if positive_diffs else 0
    except:
        return 0


@register.filter
def max_negative_difference(queryset):
    """بیشترین کسری موجودی"""
    try:
        negative_diffs = [abs(item.difference) for item in queryset if item.difference < 0]
        return max(negative_diffs) if negative_diffs else 0
    except:
        return 0


@register.filter
def unique(queryset, field_name):
    """گرفتن مقادیر یکتا از یک فیلد"""
    try:
        seen = set()
        unique_items = []
        for item in queryset:
            value = getattr(item, field_name)
            if value not in seen:
                seen.add(value)
                unique_items.append(item)
        return unique_items
    except:
        return queryset