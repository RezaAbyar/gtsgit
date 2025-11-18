from django import forms
from .models import LockModel, GsModel, Pump, Status
import jdatetime


class InstallLockForm(forms.Form):
    meeting_number = forms.CharField(
        label="شماره صورتجلسه",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'meeting_number',
            'placeholder': 'شماره صورتجلسه را وارد کنید'
        })
    )
    gs = forms.ModelChoiceField(
        queryset=GsModel.objects.none(),
        label="نام جایگاه",
        required=True
    )

    lock_type = forms.ChoiceField(
        choices=[('install', 'نصبی'), ('hot', 'داغی')],
        label="نوع پلمپ",
        required=True
    )

    serial = forms.CharField(
        label="سریال پلمپ",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'serial_input',
            'placeholder': 'برای پلمپ داغی وارد کنید'
        })
    )
    serial_select = forms.ModelChoiceField(
        queryset=LockModel.objects.none(),
        label="سریال پلمپ (نصبی)",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'serial_select'
        })
    )
    description = forms.CharField(
        label="توضیحات",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # فیلتر سریال‌های موجود برای تکنسین (برای پلمپ نصبی)
        if user and hasattr(user, 'owner'):

            self.fields['serial_select'].queryset = LockModel.objects.filter(
                owner=user.owner,
                status_id__in=[4, 8]  # وضعیت‌های قابل استفاده برای نصب
            )

        # تنظیم فرمت نمایش برای فیلد جایگاه
        self.fields['gs'].label_from_instance = lambda obj: f"{obj.gsid} - {obj.name}"

    # def clean_date(self):
    #     date_str = self.cleaned_data['date']
    #     try:
    #         # تبدیل تاریخ شمسی به میلادی
    #         year, month, day = map(int, date_str.split('/'))
    #         jalali_date = jdatetime.date(year, month, day)
    #         gregorian_date = jalali_date.togregorian()
    #         return gregorian_date
    #     except (ValueError, IndexError):
    #         raise forms.ValidationError("فرمت تاریخ نامعتبر است. فرمت صحیح: 1403/01/01")

    def clean(self):
        cleaned_data = super().clean()
        lock_type = cleaned_data.get('lock_type')
        serial_input = cleaned_data.get('serial')
        serial_select = cleaned_data.get('serial_select')

        # اعتبارسنجی بر اساس نوع پلمپ
        if lock_type == 'install':
            if not serial_select:
                raise forms.ValidationError("برای پلمپ نصبی باید سریال را از لیست انتخاب کنید.")
            cleaned_data['serial'] = serial_select
        else:  # داغی
            if not serial_input:
                raise forms.ValidationError("برای پلمپ داغی باید سریال را وارد کنید.")
            if len(serial_input) < 3:
                raise forms.ValidationError("سریال وارد شده نامعتبر است.")

        return cleaned_data


class SoratJalaseForm(forms.Form):
    meeting_number = forms.CharField(
        label="شماره صورتجلسه",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره صورتجلسه را وارد کنید'
        })
    )

    gs = forms.ModelChoiceField(
        queryset=GsModel.objects.none(),
        label="نام جایگاه",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.CharField(
        label="تاریخ (شمسی)",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1403/01/01',
            'data-jdp': ''
        })
    )

    soratjalase = forms.FileField(
        label="آپلود صورتجلسه",
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg'
        })
    )

    description = forms.CharField(
        label="توضیحات",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات مربوط به صورتجلسه'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # تنظیم کوئری‌ست جایگاه‌ها
        # if user:
        #     self.fields['gs'].queryset = GsModel.object_role.c_gsmodel(request)

        # تنظیم فرمت نمایش برای فیلد جایگاه
        # self.fields['gs'].label_from_instance = lambda obj: f"{obj.gsid} - {obj.name}"

    def clean_date(self):
        date_str = self.cleaned_data['date']
        try:
            # تبدیل تاریخ شمسی به میلادی
            year, month, day = map(int, date_str.split('/'))
            jalali_date = jdatetime.date(year, month, day)
            gregorian_date = jalali_date.togregorian()
            return gregorian_date
        except (ValueError, IndexError):
            raise forms.ValidationError("فرمت تاریخ نامعتبر است. فرمت صحیح: 1403/01/01")