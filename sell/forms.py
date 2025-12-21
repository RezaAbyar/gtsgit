from django import forms
from .models import ParametrGs, SellModel, Mojodi
import jdatetime


class ParametrGssForm(forms.ModelForm):
    class Meta:
        model = ParametrGs
        fields = ['oildepot', 'distance', 'normaltime', 'traffictime', ]


class UploadSoratjalaseForm(forms.ModelForm):
    class Meta:
        model = SellModel
        fields = ['image', ]


class MojodiForm(forms.ModelForm):
    tarikh = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'tarikh-input',
            'autocomplete': 'off'
        }),
        label='تاریخ'
    )

    class Meta:
        model = Mojodi
        fields = ['gs', 'tarikh', 'benzin', 'super', 'gaz']
        widgets = {
            'gs': forms.Select(attrs={'class': 'form-control'}),
            'benzin': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'super': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'gaz': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        labels = {
            'gs': 'جایگاه',
            'benzin': 'بنزین (لیتر)',
            'super': 'سوپر (لیتر)',
            'gaz': 'گاز (لیتر)',
        }

    def clean_tarikh(self):
        tarikh_str = self.cleaned_data['tarikh']
        try:
            # تبدیل تاریخ شمسی به میلادی
            tarikh_parts = tarikh_str.split('/')
            if len(tarikh_parts) != 3:
                raise forms.ValidationError("فرمت تاریخ صحیح نیست. فرمت صحیح: YYYY/MM/DD")

            year = int(tarikh_parts[0])
            month = int(tarikh_parts[1])
            day = int(tarikh_parts[2])

            # تبدیل به تاریخ شمسی و سپس میلادی
            jdate = jdatetime.date(year, month, day)
            gregorian_date = jdate.togregorian()

            return gregorian_date
        except (ValueError, IndexError):
            raise forms.ValidationError("تاریخ وارد شده معتبر نیست.")
