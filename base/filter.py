import django_filters
from django import forms
from openpyxl.descriptors import Max

from pay.models import StatusRef
from .models import *


class GsFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    product = django_filters.ModelMultipleChoiceFilter(field_name='gsall__product_id', queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)
    ipc = django_filters.ModelMultipleChoiceFilter(queryset=Ipc.objects.all(),
                                                   widget=forms.CheckboxSelectMultiple)
    rack = django_filters.ModelMultipleChoiceFilter(queryset=Rack.objects.all(),
                                                    widget=forms.CheckboxSelectMultiple)
    operator = django_filters.ModelMultipleChoiceFilter(queryset=Operator.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple)
    modem = django_filters.ModelMultipleChoiceFilter(queryset=Modem.objects.all(),
                                                     widget=forms.CheckboxSelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(queryset=Status.objects.all(),
                                                      widget=forms.CheckboxSelectMultiple)

    montakhab = django_filters.BooleanFilter(field_name='is_montakhab', lookup_expr='exact',
                                             widget=forms.NullBooleanSelect)
    isonline = django_filters.BooleanFilter(field_name='isonline', lookup_expr='exact',
                                            widget=forms.NullBooleanSelect)
    isbank = django_filters.BooleanFilter(field_name='isbank', lookup_expr='exact',
                                          widget=forms.NullBooleanSelect)
    ispaystation = django_filters.BooleanFilter(field_name='ispaystation', lookup_expr='exact',
                                                widget=forms.NullBooleanSelect)
    isbankmeli = django_filters.BooleanFilter(field_name='isbankmeli', lookup_expr='exact',
                                              widget=forms.NullBooleanSelect)
    iscoding = django_filters.BooleanFilter(field_name='iscoding', lookup_expr='exact',
                                            widget=forms.NullBooleanSelect)
    gsstatus = django_filters.ModelMultipleChoiceFilter(queryset=GsStatus.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple)


class TicketFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area_id', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)
    gs = django_filters.ModelMultipleChoiceFilter(field_name='gs_id', queryset=GsModel.objects.all(),
                                                  widget=forms.SelectMultiple)
    pump = django_filters.NumberFilter(field_name='Pump__number'
                                                    )
    product = django_filters.ModelMultipleChoiceFilter(field_name='Pump__product', queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)
    organization = django_filters.ModelMultipleChoiceFilter(field_name='organization',
                                                            queryset=Organization.objects.all(),
                                                            widget=forms.SelectMultiple)
    failurecategory = django_filters.ModelMultipleChoiceFilter(field_name='failure__failurecategory',
                                                               queryset=FailureCategory.objects.all(),
                                                               widget=forms.SelectMultiple)
    failure = django_filters.ModelMultipleChoiceFilter(field_name='failure', queryset=FailureSub.objects.all(),
                                                       widget=forms.SelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(field_name='status', queryset=StatusTicket.objects.all(),
                                                      widget=forms.SelectMultiple)
    reply = django_filters.ModelMultipleChoiceFilter(field_name='reply', queryset=Reply.objects.all(),
                                                     widget=forms.SelectMultiple)
    star1 = django_filters.NumberFilter(field_name='star', lookup_expr='gte',
                                        )
    star2 = django_filters.NumberFilter(field_name='star', lookup_expr='lte',
                                        )
    countnosell = django_filters.NumberFilter(field_name='countnosell', lookup_expr='gt',
                                              )
    actioner = django_filters.ModelMultipleChoiceFilter(field_name='actioner', queryset=Owner.objects.filter(
        role__role__in=['tek', 'test', 'fani', 'zone']),
                                                        widget=forms.SelectMultiple)

    choice1 = {
        ('date', 'تاریخ ایجاد'),
        ('date2', 'تاریخ اقدام'),
        ('info', 'شرح خرابی'),
        ('gsid', 'شناسه جایگاه'),
        ('zone', 'منطقه'),

    }

    gsid = django_filters.ChoiceFilter(choices=choice1, method='gsid_filter')

    def gsid_filter(self, queryset, name, value):
        data = 'create'
        if value == 'date':
            data = '-create'
        if value == 'date2':
            data = '-closedate'
        if value == 'info':
            data = 'failure__info'
        if value == 'gsid':
            data = 'gs__gsid'
        if value == 'zone':
            data = 'gs__area__zone'
        return queryset.order_by(data)

    is_initial = django_filters.BooleanFilter(
        method='filter_initial',
        label='نمایش تیکت‌های Initial',
        widget=forms.CheckboxInput,
    )

    def filter_initial(self, queryset, name, value):
        if value:
            return queryset.filter(failure__enname='initial')
        return queryset

    def __init__(self, *args, **kwargs):
        # دریافت request از kwargs
        request = kwargs.pop('request', None)
        super(TicketFilter, self).__init__(*args, **kwargs)

        # تنظیم queryset بر اساس request
        if request:
            if request.user.owner.role.role in ['tek', 'gs']:
                self.filters['gs'].queryset = GsModel.objects.filter(gsowner__owner_id=request.user.owner.id)
            elif request.user.owner.role.role == 'zone':
                self.filters['gs'].queryset = GsModel.objects.filter(area__zone_id=request.user.owner.zone.id)
                self.filters['area'].queryset = Area.objects.filter(zone_id=request.user.owner.zone.id)
            elif request.user.owner.role.role == 'area':
                self.filters['gs'].queryset = GsModel.objects.filter(area_id=request.user.owner.area.id)


class GSFilters(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)


class UserFilters(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)
    role = django_filters.ModelMultipleChoiceFilter(queryset=Role.objects.all(),
                                                    widget=forms.SelectMultiple)
    refrence = django_filters.ModelMultipleChoiceFilter(queryset=Refrence.objects.all(),
                                                        widget=forms.SelectMultiple)
    active = django_filters.BooleanFilter(field_name='active', lookup_expr='exact',
                                          widget=forms.NullBooleanSelect)

    choice1 = {
        ('create', 'تاریخ ایجاد'),
        ('last_login', 'آخرین ورود'),
        ('zone', 'منطقه'),

    }
    gsid = django_filters.ChoiceFilter(choices=choice1, method='gsid_filter')

    def gsid_filter(self, queryset, name, value):
        data = '-user__last_login'
        if value == 'last_login':
            data = '-user__last_login'
        if value == 'create':
            data = '-create'
        if value == 'zone':
            data = 'zone'
        return queryset.order_by(data)


class StoreFilters(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='zone', queryset=Zone.objects.all(),
                                                    widget=forms.SelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(field_name='status', queryset=StatusRef.objects.all(),
                                                      widget=forms.SelectMultiple)
    storage = django_filters.ModelMultipleChoiceFilter(field_name='storage',
                                                       queryset=Storage.objects.all().order_by('sortid'),
                                                       widget=forms.SelectMultiple)


class NazelFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)
    product = django_filters.ModelMultipleChoiceFilter(field_name='product', queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(field_name='gs__status', queryset=Status.objects.all(),
                                                      widget=forms.SelectMultiple)
    statuspump = django_filters.ModelMultipleChoiceFilter(field_name='status', queryset=Statuspump.objects.all(),
                                                          widget=forms.SelectMultiple)
    pumpbrand = django_filters.ModelMultipleChoiceFilter(field_name='pumpbrand', queryset=PumpBrand.objects.all(),
                                                         widget=forms.SelectMultiple)


class IpcFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='updatedate', lookup_expr='gte')
    scan_date = django_filters.DateFilter(field_name='update', lookup_expr='lte')
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(field_name='gs__status', queryset=Status.objects.all(),
                                                      widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)
    product = django_filters.ModelMultipleChoiceFilter(field_name='gs__gsall__product_id',
                                                       queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)
    ck_dashboard_version = django_filters.BooleanFilter(field_name='ck_dashboard_version', lookup_expr='exact',
                                                        widget=forms.NullBooleanSelect)

    ck_rpm_version = django_filters.BooleanFilter(field_name='ck_rpm_version', lookup_expr='exact',
                                                  widget=forms.NullBooleanSelect)

    ck_pt_version = django_filters.BooleanFilter(field_name='ck_pt_version', lookup_expr='exact',
                                                 widget=forms.NullBooleanSelect)
    ck_pt_online = django_filters.BooleanFilter(field_name='ck_pt_online', lookup_expr='exact',
                                                widget=forms.NullBooleanSelect)
    ck_quta_table_version = django_filters.BooleanFilter(field_name='ck_quta_table_version', lookup_expr='exact',
                                                         widget=forms.NullBooleanSelect)
    ck_price_table_version = django_filters.BooleanFilter(field_name='ck_price_table_version', lookup_expr='exact',
                                                          widget=forms.NullBooleanSelect)
    ck_zone_table_version = django_filters.BooleanFilter(field_name='ck_zone_table_version', lookup_expr='exact',
                                                         widget=forms.NullBooleanSelect)
    ck_blacklist_version = django_filters.BooleanFilter(field_name='ck_blacklist_version', lookup_expr='exact',
                                                        widget=forms.NullBooleanSelect)
    ck_blacklist_count = django_filters.BooleanFilter(field_name='ck_blacklist_count', lookup_expr='exact',
                                                      widget=forms.NullBooleanSelect)
    sam = django_filters.BooleanFilter(field_name='sam', lookup_expr='exact',
                                       widget=forms.NullBooleanSelect)
    datacenter = django_filters.BooleanFilter(field_name='datacenter', lookup_expr='exact',
                                              widget=forms.NullBooleanSelect)
    modem = django_filters.BooleanFilter(field_name='modem', lookup_expr='exact',
                                         widget=forms.NullBooleanSelect)

    fasb = django_filters.BooleanFilter(field_name='fasb', lookup_expr='exact',
                                        widget=forms.NullBooleanSelect)

    poler = django_filters.BooleanFilter(field_name='poler', lookup_expr='exact',
                                         widget=forms.NullBooleanSelect)

    internet = django_filters.BooleanFilter(field_name='internet', lookup_expr='exact',
                                            widget=forms.NullBooleanSelect)

    mellatmodem = django_filters.BooleanFilter(field_name='mellatmodem', lookup_expr='exact',
                                               widget=forms.NullBooleanSelect)

    contradiction = django_filters.BooleanFilter(field_name='contradiction', lookup_expr='exact',
                                                 widget=forms.NullBooleanSelect)

    gs_version_filter = django_filters.BooleanFilter(
        method='filter_gs_version',
        label='وضعیت GS Version',
        widget=forms.Select(choices=[
            ('unknown', 'همه'),
            ('True', 'دارای مقدار'),
            ('False', 'بدون مقدار یا صفر'),
        ])
    )

    imagever_filter = django_filters.BooleanFilter(
        method='filter_imagever',
        label='وضعیت Image Version',
        widget=forms.Select(choices=[
            ('unknown', 'همه'),
            ('True', 'دارای مقدار'),
            ('False', 'بدون مقدار یا صفر'),
        ])
    )

    choice1 = {
        ('area', 'نام ناحیه'),
        ('gsid', 'GSID'),
        ('updatedate', 'آخرین تاریخ اسکن'),
        ('last_connection', 'آخرین ارتباط با دیتاسنتر'),
        ('ck_dashboard_version', 'نگارش داشبورد'),
        ('ck_rpm_version', 'نگارش RPM'),
        ('ck_pt_version', 'نگارش PT'),
        ('ck_pt_online', 'مغایرت جایگاه آنلاین'),
        ('ck_quta_table_version', 'نگارش جدول سهمیه'),
        ('ck_price_table_version', 'نگارش جدول قیمت'),
        ('ck_blacklist_version', 'نگارش جدول بلک لیست'),
        ('ck_blacklist_count', 'مغایرت تعداد لیست سیاه'),
        ('ck_zone_table_version', 'نگارش جدول منطقه ایی'),
    }

    gsid = django_filters.ChoiceFilter(choices=choice1, method='ipc_filter')

    def ipc_filter(self, queryset, name, value):
        data = 'ck_dashboard_version'
        if value == 'area':
            data = 'gs__area_id'
        if value == 'gsid':
            data = 'gs__gsid'
        if value == 'last_connection':
            data = '-last_connection'
        if value == 'updatedate':
            data = '-updatedate'
        if value == 'ck_dashboard_version':
            data = '-ck_dashboard_version'
        if value == 'ck_rpm_version':
            data = 'ck_rpm_version'
        if value == 'ck_pt_version':
            data = 'ck_pt_version'
        if value == 'ck_quta_table_version':
            data = 'ck_quta_table_version'
        if value == 'ck_price_table_version':
            data = 'ck_price_table_version'
        if value == 'ck_blacklist_version':
            data = 'ck_blacklist_version'
        if value == 'ck_pt_online':
            data = 'ck_pt_online'
        if value == 'ck_blacklist_count':
            data = 'ck_blacklist_count'
        if value == 'ck_zone_table_version':
            data = 'ck_zone_table_version'
        return queryset.order_by(data)

    def filter_gs_version(self, queryset, name, value):
        if value == True:
            return queryset.exclude(gs_version__isnull=True).exclude(gs_version__exact='0')
        elif value == False:
            return queryset.filter(gs_version__exact=0)
        return queryset

    def filter_imagever(self, queryset, name, value):
        if value == True:
            return queryset.exclude(imagever__isnull=True).exclude(imagever__exact='0')
        elif value == False:
            return queryset.filter(Q(imagever__isnull=True) | Q(imagever__exact='0'))
        return queryset
