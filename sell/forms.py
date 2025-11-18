from django import forms
from .models import ParametrGs, SellModel


class ParametrGssForm(forms.ModelForm):
    class Meta:
        model = ParametrGs
        fields = ['oildepot', 'distance', 'normaltime', 'traffictime', ]


class UploadSoratjalaseForm(forms.ModelForm):
    class Meta:
        model = SellModel
        fields = ['image', ]

