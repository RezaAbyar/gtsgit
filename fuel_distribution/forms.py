from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django_jalali.forms import jDateField

from .models import (
    UserDistributionProfile, SuperFuelImport, ImportToDistributor,
    DistributorGasStation, DistributionToGasStation, FuelDistributionReport,
    FuelStock
)

from base.models import GsModel, Owner, Company


class UserDistributionProfileForm(forms.ModelForm):
    """فرم پروفایل کاربر توزیع"""

    class Meta:
        model = UserDistributionProfile
        fields = ['role', 'company']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'id': 'role-select'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control',
                'id': 'company-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all()


class SuperFuelImportForm(forms.ModelForm):
    """فرم ثبت واردات بنزین سوپر"""

    class Meta:
        model = SuperFuelImport
        fields = [
            'amount_liters', 'tracking_number',
            'document_number', 'description'
        ]
        widgets = {
            'amount_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 1
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره رهگیری واردات'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره سند واردات'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات (اختیاری)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_tracking_number(self):
        tracking_number = self.cleaned_data['tracking_number']
        if SuperFuelImport.objects.filter(tracking_number=tracking_number).exists():
            raise ValidationError('این شماره رهگیری قبلاً ثبت شده است.')
        return tracking_number



    def clean_amount_liters(self):
        amount = self.cleaned_data['amount_liters']
        if amount <= 0:
            raise ValidationError('مقدار باید بزرگتر از صفر باشد.')
        return amount


class ImportToDistributorForm(forms.ModelForm):
    """فرم توزیع به توزیع‌کننده"""


    class Meta:
        model = ImportToDistributor
        fields = [
            'fuel_import', 'distributor',
            'amount_liters', 'price_per_liter', 'document_number',
            'transport_info', 'notes'
        ]
        widgets = {
            'fuel_import': forms.Select(attrs={
                'class': 'form-control',
                'id': 'fuel-import-select'
            }),
            'distributor': forms.Select(attrs={
                'class': 'form-control',
                'id': 'distributor-select'
            }),
            'amount_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 1,
                'id': 'amount-liters-input'
            }),
            'price_per_liter': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 100,
                'placeholder': 'ریال'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره سند توزیع'
            }),
            'transport_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اطلاعات حمل (اختیاری)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات (اختیاری)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            # فقط توزیع‌کننده‌ها را نمایش بده
            self.fields['distributor'].queryset = Owner.objects.filter(
                distribution_profile__role='distributor'
            )

    def clean(self):
        cleaned_data = super().clean()
        fuel_import = cleaned_data.get('fuel_import')
        amount_liters = cleaned_data.get('amount_liters')

        if fuel_import and amount_liters:
            if amount_liters > fuel_import.remaining_amount:
                raise ValidationError(
                    f'مقدار توزیع نمی‌تواند بیشتر از مقدار باقی‌مانده ({fuel_import.remaining_amount} لیتر) باشد.'
                )

        return cleaned_data




class DistributorGasStationForm(forms.ModelForm):
    """فرم افزودن جایگاه به زیرمجموعه توزیع‌کننده"""


    class Meta:
        model = DistributorGasStation
        fields = ['gas_station', 'contract_number', 'notes']
        widgets = {
            'gas_station': forms.Select(attrs={
                'class': 'form-control',
                'id': 'gas-station-select'
            }),
            'contract_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره قرارداد (اختیاری)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات (اختیاری)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.distributor = kwargs.pop('distributor', None)
        super().__init__(*args, **kwargs)

        if self.distributor:
            # جایگاه‌هایی که قبلاً به این توزیع‌کننده اضافه نشده‌اند
            existing_stations = DistributorGasStation.objects.filter(
                distributor=self.distributor
            ).values_list('gas_station_id', flat=True)

            stations_queryset = GsModel.objects.exclude(
                id__in=existing_stations
            )

            # ایجاد لیست انتخاب با فرمت مناسب
            choices = [(gs.id, f"{gs.gsid} - {gs.name}") for gs in stations_queryset]
            self.fields['gas_station'].choices = choices
            self.fields['gas_station'].queryset = stations_queryset




class DistributionToGasStationForm(forms.ModelForm):
    """فرم توزیع به جایگاه"""
    class Meta:
        model = DistributionToGasStation
        fields = [
            'distributor_distribution', 'distributor_gas_station',
            'amount_liters', 'price_per_liter',
            'delivery_document', 'driver_info', 'vehicle_info', 'notes'
        ]
        widgets = {
            'distributor_distribution': forms.Select(attrs={
                'class': 'form-control',
                'id': 'distributor-distribution-select'
            }),
            'distributor_gas_station': forms.Select(attrs={
                'class': 'form-control',
                'id': 'distributor-gas-station-select'
            }),
            'amount_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 1,
                'id': 'amount-liters-input'
            }),
            'price_per_liter': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 100,
                'placeholder': 'ریال'
            }),
            'delivery_document': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره سند تحویل (اختیاری)'
            }),
            'driver_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اطلاعات راننده (اختیاری)'
            }),
            'vehicle_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اطلاعات وسیله نقلیه (اختیاری)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات (اختیاری)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.distributor = kwargs.pop('distributor', None)
        self.station = kwargs.pop('station', None)
        super().__init__(*args, **kwargs)

        if self.distributor:
            # فقط توزیع‌های متعلق به این توزیع‌کننده
            self.fields['distributor_distribution'].queryset = ImportToDistributor.objects.filter(
                distributor=self.distributor
            )

            # فقط جایگاه‌های زیرمجموعه این توزیع‌کننده
            self.fields['distributor_gas_station'].queryset = DistributorGasStation.objects.filter(
                distributor=self.distributor,
                is_active=True
            )

            if self.station:
                self.fields['distributor_gas_station'].initial = self.station
                self.fields['distributor_gas_station'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        distributor_distribution = cleaned_data.get('distributor_distribution')
        amount_liters = cleaned_data.get('amount_liters')

        if distributor_distribution and amount_liters:
            # محاسبه مقدار باقی‌مانده از این توزیع
            distributed_amount = DistributionToGasStation.objects.filter(
                distributor_distribution=distributor_distribution,
                status__in=['scheduled', 'in_transit', 'delivered']
            ).aggregate(total=Sum('amount_liters'))['total'] or 0

            remaining_amount = distributor_distribution.amount_liters - distributed_amount

            if amount_liters > remaining_amount:
                raise ValidationError(
                    f'مقدار توزیع نمی‌تواند بیشتر از مقدار باقی‌مانده ({remaining_amount} لیتر) باشد.'
                )

        return cleaned_data




class FuelDistributionReportForm(forms.ModelForm):
    """فرم تولید گزارش"""
    period_start = jDateField(
        label="شروع دوره",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'YYYY/MM/DD',
            'autocomplete': 'off'
        })
    )

    period_end = jDateField(
        label="پایان دوره",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'YYYY/MM/DD',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = FuelDistributionReport
        fields = ['report_type', 'period_start', 'period_end', 'company']
        widgets = {
            'report_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'report-type-select'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control',
                'id': 'company-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and hasattr(self.user, 'distribution_profile'):
            profile = self.user.distribution_profile
            self.fields['company'].initial = profile.company

            if profile.role == 'importer':
                self.fields['company'].queryset = Company.objects.filter(id=profile.company.id)
            else:
                # برای سایر نقش‌ها، همه شرکت‌ها را نشان بده
                self.fields['company'].queryset = Company.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')

        if period_start and period_end:
            if period_start > period_end:
                raise ValidationError('تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.')

            if period_end > timezone.now().date():
                raise ValidationError('تاریخ پایان نمی‌تواند در آینده باشد.')

        return cleaned_data


class FuelStockUpdateForm(forms.ModelForm):
    """فرم به‌روزرسانی موجودی"""

    class Meta:
        model = FuelStock
        fields = ['current_stock']
        widgets = {
            'current_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            }),
        }

    def clean_current_stock(self):
        current_stock = self.cleaned_data['current_stock']
        if current_stock < 0:
            raise ValidationError('موجودی نمی‌تواند منفی باشد.')
        return current_stock


