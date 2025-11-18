from django import forms
from .models import UploadExcel, Ticket, Owner, GsModel, Area, OwnerChild, OwnerFiles, ReInitial, UploadFiles, City, \
    Makhzan_sejjeli, Pump_sejjeli, GsModel_sejjeli, NewSejelli, Makhzan, Parametrs


class UserRegisterationForm(forms.Form):
    username = forms.CharField(label='شماره موبایل', widget=forms.TextInput(attrs={'class': 'form-control'}))
    # first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    first_name = forms.CharField(label='نام', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='نام خانوادگی', widget=forms.TextInput(attrs={'class': 'form-control'}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserLoginForm(forms.Form):
    username = forms.CharField(label='شماره موبایل', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class open_excel(forms.ModelForm):
    class Meta:
        model = UploadExcel
        fields = {'filepath', }
        widgets = {
            'filepath': forms.widgets.FileInput(attrs={
                'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'})
        }


class open_excel_img(forms.ModelForm):
    class Meta:
        model = GsModel
        fields = {'koroki', }
        widgets = {
            'filepath': forms.widgets.FileInput(attrs={
                'accept': 'image/jpeg'})
        }


class open_excel_sejelli(forms.ModelForm):
    class Meta:
        model = GsModel
        fields = {'sejelli', }
        widgets = {
            'filepath': forms.widgets.FileInput(attrs={
                'accept': 'image/jpeg'})
        }


class open_excel_flouk(forms.ModelForm):
    class Meta:
        model = GsModel
        fields = {'flock', }
        widgets = {
            'filepath': forms.widgets.FileInput(attrs={
                'accept': 'image/jpeg'})
        }


class FormReInitial(forms.ModelForm):
    class Meta:
        model = ReInitial
        fields = {'gs', 'quiz1', 'quiz2', 'quiz3', 'info_quiz3', 'quiz5', 'ups_min', 'ups_kva',
                  'ups_battri', 'ups_status_battri', 'quiz6', 'info_quiz6', 'quiz8', 'quiz9',
                  'quiz11', 'quiz12', 'quiz14', 'name',
                  }


class open_excel_card(forms.ModelForm):
    class Meta:
        model = UploadExcel
        fields = {'filepath', }
        widgets = {
            'filepath': forms.widgets.FileInput(attrs={
                'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'})
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['gs', 'failure', 'descriptionowner']


class SearchForm(forms.Form):
    search = forms.CharField(label='جستجو', required=False)


class ImageProfile(forms.ModelForm):
    class Meta:
        model = Owner
        fields = {'img', }


class GsEditForm(forms.ModelForm):
    class Meta:
        model = GsModel
        fields = ['gsid', 'name', 'address', 'phone', 'area', 'active']


class verifyForm(forms.Form):
    code = forms.IntegerField()


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['phone', 'address', 'lat', 'long', ]


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', ]


class TekProfileForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['accountnumber', 'shsh', 'sodor', 'father', 'mysex',
                  'khedmat', 'education', 'place_of_birth', 'date_of_birth', 'marital_status',
                  'start_date', ]


class OwnerChildForm(forms.ModelForm):
    class Meta:
        model = OwnerChild
        fields = ['name', 'codemeli', 'marid', 'sex',
                  'khedmat', 'img', 'active']


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = OwnerFiles
        fields = ['img', ]


class UploadUsersFile(forms.ModelForm):
    class Meta:
        model = UploadFiles
        fields = 'file',


class GsModelSejjeliForm(forms.ModelForm):
    class Meta:
        model = GsModel_sejjeli
        exclude = ['newsejelli', 'gs', 'gsid', 'create']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class PumpSejjeliForm(forms.ModelForm):
    class Meta:
        model = Pump_sejjeli
        exclude = ['newsejelli', 'gs', 'create']
        widgets = {
            'number': forms.NumberInput(attrs={'min': 1}),
            'sakoo': forms.NumberInput(attrs={'min': 1}),
            'tolombe': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        # دریافت sejelli_id از kwargs اگر وجود دارد
        sejelli_id = kwargs.pop('sejelli_id', None)
        super(PumpSejjeliForm, self).__init__(*args, **kwargs)

        # اگر sejelli_id وجود داشت، فیلد makhzan را فیلتر کنید
        if sejelli_id:
            sejelli = NewSejelli.objects.get(id=sejelli_id)
            self.initial['makhzan_choices'] = Makhzan_sejjeli.objects.filter(gs=sejelli.gs)


class MakhzanSejjeliForm(forms.ModelForm):
    class Meta:
        model = Makhzan_sejjeli
        exclude = ['newsejelli', 'gs', 'create_time']
        widgets = {
            'number': forms.NumberInput(attrs={'min': 1}),
            'zarfyat': forms.NumberInput(attrs={'min': 0}),
        }


class ParametrsForm(forms.ModelForm):
    class Meta:
        model = Parametrs
        fields = '__all__'
        widgets = {
            'dashboard_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1.2.3'
            }),
            'rpm_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 2.1.0'
            }),
            'pt_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 3.0.1'
            }),
            'quta_table_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1.0.0'
            }),
            'zone_table_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 2.1.5'
            }),
            'price_table_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1.3.2'
            }),
            'blacklist_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1.0.0'
            }),
            'online_pt_version': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'happyday': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1403/07/15'
            }),
            'mediaurl': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/media'
            }),
            'msg': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'پیام سیستم برای نمایش به کاربران...'
            }),
        }
        labels = {
            'dashboard_version': 'نسخه داشبورد',
            'rpm_version': 'نسخه RPM',
            'pt_version': 'نسخه PT',
            'quta_table_version': 'نسخه جدول سهمیه',
            'zone_table_version': 'نسخه جدول منطقه‌ای',
            'price_table_version': 'نسخه جدول قیمت',
            'blacklist_version': 'نسخه لیست سیاه',
            'online_pt_version': 'نسخه آنلاین PT',
            'bypass_sms': 'غیرفعال کردن سامانه پیامک',
            'is_arbain': 'فعال کردن داشبورد اربعین',
            'autoticketbyqrcode': 'تیکت اتوماتیک با QR Code',
            'isgps': 'الزام دریافت موقعیت جغرافیایی',
            'isacceptforbuy': 'فعال کردن تایید برای خرید',
            'is_saf': 'فعال کردن حالت صف',
            'ispeykarbandi': 'فعال کردن کد پیکربندی',
            'ismohasebat': 'محاسبه اتوماتیک آیتم‌های حقوق',
            'func': 'تسک تعداد تیکت روزانه',
            'moghayerat': 'تسک مغایرت مناطق',
            'btmt': 'ثبت فروش',
            'btmt2': 'نمایش آیکون پشتیبانی',
            'is_event': 'نمایش مناسبت‌ها در لاگین',
            'happyday': 'تاریخ افتتاح GTS',
            'mediaurl': 'آدرس مدیا',
            'msg': 'پیام سیستم',
        }
        help_texts = {
            'bypass_sms': 'در صورت فعال بودن، سامانه پیامک از دور خارج می‌شود',
            'autoticketbyqrcode': 'پس از اسکن رمزینه در صورت مغایرت، تیکت اتوماتیک صادر شود',
            'isgps': 'دریافت موقعیت جغرافیایی برای برخی عملیات الزامی باشد',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # برای فیلدهای بولین از چک‌باکس استفاده می‌کنیم
        boolean_fields = [
            'bypass_sms', 'is_arbain', 'autoticketbyqrcode', 'isgps',
            'isacceptforbuy', 'is_saf', 'ispeykarbandi', 'ismohasebat',
            'func', 'moghayerat', 'btmt', 'btmt2', 'is_event'
        ]

        for field_name in boolean_fields:
            self.fields[field_name].widget = forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })