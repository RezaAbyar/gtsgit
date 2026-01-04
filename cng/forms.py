from django import forms
from .models import CNGStation, Equipment, StationMeter, EquipmentSupplier, Capacity
from base.models import Zone, Area, City


class CNGStationForm(forms.ModelForm):
    class Meta:
        model = CNGStation
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'ownership_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فیلدهای اختیاری
        for field in ['old_code', 'owner_name']:
            self.fields[field].required = False


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        exclude = ['created_at', 'updated_at', 'station']  # station را خارج کنید چون در view تنظیم می‌شود
        widgets = {
            'removal_reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'equipment_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'dispenser_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'installation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'temporary_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'permanent_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority_letter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'priority_letter_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'removal_letter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'removal_letter_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_letter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_letter_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transfer_letter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'transfer_letter_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.Select(attrs={'class': 'form-control'}),
            'input_pressure': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transport_status': forms.Select(attrs={'class': 'form-control'}),
            'usage_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اضافه کردن کلاس form-control به همه فیلدها
        for field_name, field in self.fields.items():
            if field_name not in ['permanent_delivery', 'used_equipment', 'non_private_transferred']:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
            elif field_name in ['permanent_delivery', 'used_equipment', 'non_private_transferred']:
                field.widget.attrs['class'] = 'form-check-input'


class StationMeterForm(forms.ModelForm):
    class Meta:
        model = StationMeter
        fields = ['meter_number', 'fee_type']
        widgets = {
            'meter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'fee_type': forms.Select(attrs={'class': 'form-control'}),
        }


class EquipmentSupplierForm(forms.ModelForm):
    class Meta:
        model = EquipmentSupplier
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CapacityForm(forms.ModelForm):
    class Meta:
        model = Capacity
        fields = '__all__'
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
        }