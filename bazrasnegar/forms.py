from django import forms

from bazrasnegar.models import BazrasNegar


class BazrasNegarSearchForm(forms.Form):
    query = forms.CharField(
        label='جستجو',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'عنوان، شماره، تاریخ یا متن اطلاعیه...',
            'class': 'form-control'
        })
    )


class BazrasNegarForm(forms.ModelForm):
    class Meta:
        model = BazrasNegar
        fields = ['number', 'tarikh', 'title', 'info', 'file']
        labels = {
            'number': 'شماره اطلاعیه',
            'tarikh': 'تاریخ',
            'title': 'عنوان',
            'info': 'متن اطلاعیه',
            'file': 'فایل پیوست',
        }
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره اطلاعیه را وارد کنید'}),
            'tarikh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'تاریخ را وارد کنید'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان را وارد کنید'}),
            'info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'متن اطلاعیه را وارد کنید'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }