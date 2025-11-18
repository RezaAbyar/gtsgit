# stations/forms.py
from django import forms
from .models import PMChecklist
from django.utils import timezone


class PMChecklistForm(forms.ModelForm):
    class Meta:
        model = PMChecklist
        exclude = ['technician', 'check_date', 'region', 'area']
        widgets = {
            'next_check_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_ground_renewal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'unnecessary_software_desc': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'unsealed_doors': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'info_software': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'station_phones': forms.TextInput(attrs={
                'placeholder': 'شماره تلفن‌ها را با کاما جدا کنید',
                'class': 'form-control'
            }),
            'ground_voltage': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'ground_moghavemat': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'ups_backup_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'switch_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'switch_port': forms.NumberInput(attrs={'class': 'form-control'}),
            # اضافه کردن ویجت برای همه فیلدهای متنی
            'owner_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'operator_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_model': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_height': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_temperature': forms.TextInput(attrs={'class': 'form-control'}),
            'server_os_version': forms.TextInput(attrs={'class': 'form-control'}),
            'ram_size': forms.TextInput(attrs={'class': 'form-control'}),
            'hdd_size': forms.TextInput(attrs={'class': 'form-control'}),
            'battry': forms.TextInput(attrs={'class': 'form-control'}),
            'modem_type': forms.TextInput(attrs={'class': 'form-control'}),
            'sim_card_serialnumber': forms.TextInput(attrs={'class': 'form-control'}),
            'sim_card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'signal_strength': forms.TextInput(attrs={'class': 'form-control'}),
            'switch_type': forms.TextInput(attrs={'class': 'form-control'}),
            'mouse': forms.TextInput(attrs={'class': 'form-control'}),
            'monitor': forms.TextInput(attrs={'class': 'form-control'}),
            'printer': forms.TextInput(attrs={'class': 'form-control'}),
            'sam_color': forms.TextInput(attrs={'class': 'form-control'}),
            'ups_model': forms.TextInput(attrs={'class': 'form-control'}),
            'ups_battery_type': forms.TextInput(attrs={'class': 'form-control'}),
            'ups_kva': forms.TextInput(attrs={'class': 'form-control'}),
            'inspector_signature': forms.TextInput(attrs={'class': 'form-control'}),
            'station_signature': forms.TextInput(attrs={'class': 'form-control'}),
            'smart_system_signature': forms.TextInput(attrs={'class': 'form-control'}),
            # ویجت برای فیلدهای ForeignKey
            'ipc': forms.Select(attrs={'class': 'form-control'}),
            'modem': forms.Select(attrs={'class': 'form-control'}),
            'operator': forms.Select(attrs={'class': 'form-control'}),
            'thinclient_model': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.station = kwargs.pop('station', None)
        super().__init__(*args, **kwargs)

        # اضافه کردن کلاس form-control و form-check-input به همه فیلدها
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif field.widget.attrs.get('class') is None:
                field.widget.attrs['class'] = 'form-control'

        # تنظیم مقادیر پیش‌فرض از PM قبلی
        if self.station and not self.instance.pk:
            last_checklist = PMChecklist.objects.filter(station=self.station).order_by('-check_date').first()
            if last_checklist:
                # کپی کردن مقادیر از چک لیست قبلی
                for field in self.Meta.fields:
                    if field not in ['technician', 'check_date', 'region', 'area']:
                        self.initial[field] = getattr(last_checklist, field)

        if not self.instance.pk:
            self.initial['next_check_date'] = timezone.now() + timezone.timedelta(days=90)