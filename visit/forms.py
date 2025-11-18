import jdatetime
from django import forms

from jalali_date.fields import JalaliDateField

from base.models import GsModel
from .models import CertificateType, Certificate
from django import forms
from visit.models import EmergencyFueling, EmergencyPermission
from jdatetime import date as jdate

from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from base.models import GsModel
from .models import CertificateType, Certificate
from visit.models import EmergencyFueling, EmergencyPermission
from jdatetime import date as jdate


class EmergencyFuelingForm(forms.ModelForm):
    class Meta:
        model = EmergencyFueling
        fields = ['plate_number', 'plate_number1', 'plate_number2', 'plate_number3', 'liters', 'permission']
        widgets = {

            'liters': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'plate_number': 'شماره پلاک',
            'liters': 'لیتراژ تحویلی',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # فیلدها را اختیاری کنید
        self.fields['plate_number'].required = False
        self.fields['liters'].required = False


class EmergencyPermissionForm(forms.ModelForm):
    class Meta:
        model = EmergencyPermission
        fields = ['plate_number', 'plate_number1', 'plate_number2', 'plate_number3', 'station_name', 'liters']
        widgets = {
            'liters': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'plate_number': 'شماره پلاک',
            'liters': 'لیتراژ مجاز',

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request and hasattr(self.request.user, 'owner'):
            owner = self.request.user.owner

            # تعیین نوع مجوز بر اساس نقش کاربر
            if owner.role and owner.role.role == 'zone':
                self.instance.permission_type = 'region'
            elif owner.role and owner.role.role == 'area':
                self.instance.permission_type = 'area'

            # فیلتر جایگاه‌ها بر اساس منطقه/ناحیه کاربر
            if owner.zone:
                # کاربر منطقه‌ای - همه جایگاه‌های منطقه
                self.fields['station_name'].queryset = GsModel.objects.filter(
                    area__zone=owner.zone,
                    status__status=True
                ).order_by('name')
            elif owner.area:
                # کاربر ناحیه‌ای - فقط جایگاه‌های ناحیه خودش
                self.fields['station_name'].queryset = GsModel.objects.filter(
                    area=owner.area,
                    status__status=True
                ).order_by('name')
            else:
                # کاربر جایگاه - فقط جایگاه خودش
                station_name_ids = owner.gslist_set.values_list('gs_id', flat=True)
                self.fields['station_name'].queryset = GsModel.objects.filter(
                    id__in=station_name_ids,
                    status__status=True
                ).order_by('name')

    # def clean_plate_number(self):
    #     plate_number = self.cleaned_data.get('plate_number', '').replace(' ', '')
    #     if not EmergencyFueling().validate_iranian_plate(plate_number):
    #         raise forms.ValidationError('فرمت پلاک معتبر نیست. مثال صحیح: 12الف34567')
    #     return plate_number


class CertificateTypeForm(forms.ModelForm):
    class Meta:
        model = CertificateType
        fields = ['name', 'validity_period', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['gs', 'certificate_type', 'document', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gs': forms.Select(attrs={'class': 'form-control select2'}),
            'certificate_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # اگر در حالت ویرایش هستیم، فایل را اختیاری کنید
        if self.instance and self.instance.pk:
            self.fields['document'].required = False
        else:
            self.fields['document'].required = True

        if user and hasattr(user, 'owner'):
            owner = user.owner
            # محدود کردن لیست جایگاه‌ها بر اساس منطقه کاربر
            if owner.role.role == 'zone':
                self.fields['gs'].queryset = GsModel.objects.filter(
                    area__zone=owner.zone,
                    status__status=True
                ).order_by('name')
            elif owner.role.role == 'area':
                self.fields['gs'].queryset = GsModel.objects.filter(
                    area=owner.area,
                    status__status=True
                ).order_by('name')
            else:
                # برای سایر نقش‌ها همه جایگاه‌ها نمایش داده شود
                self.fields['gs'].queryset = GsModel.objects.filter(
                    status__status=True
                ).order_by('name')
            self.fields['document'].validators = [
                self.validate_file_extension,
                self.validate_file_size
            ]

    def validate_file_extension(self, value):
        import os
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        if not ext.lower() in valid_extensions:
            raise forms.ValidationError('فقط فایل‌های JPG, PNG و PDF مجاز هستند.')

    def validate_file_size(self, value):
        filesize = value.size
        if filesize > 500 * 1024:  # 500KB
            raise forms.ValidationError("حجم فایل نمی‌تواند بیشتر از 500KB باشد.")


class CertificateTypeForm(forms.ModelForm):
    class Meta:
        model = CertificateType
        fields = ['name', 'validity_period', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['gs', 'certificate_type', 'document', 'notes','cbrand']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gs': forms.Select(attrs={'class': 'form-control select2'}),
            'certificate_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'owner'):
            owner = user.owner
            # محدود کردن لیست جایگاه‌ها بر اساس منطقه کاربر
            if owner.role.role == 'zone':
                self.fields['gs'].queryset = GsModel.objects.filter(
                    area__zone=owner.zone,
                    status__status=True
                ).order_by('name')
            elif owner.role.role == 'area':
                self.fields['gs'].queryset = GsModel.objects.filter(
                    area=owner.area,
                    status__status=True
                ).order_by('name')
            elif owner.role.role in ['gs', 'tek']:
                self.fields['gs'].queryset = GsModel.objects.filter(
                    gsowner__owner_id=owner.id,
                    status__status=True
                ).order_by('name')
            else:
                # برای سایر نقش‌ها همه جایگاه‌ها نمایش داده شود
                self.fields['gs'].queryset = GsModel.objects.filter(
                    status__status=True
                ).order_by('name')
