from django import forms
from .models import Repair, ImgSerial, StoreList, RepairStoreName, RepairRole
from .models_repaire import Repaires, RepaireStores


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['repairstore', 'valuecount']


class ImageStore(forms.ModelForm):
    class Meta:
        model = ImgSerial
        fields = ['img', ]


class StoreListForm(forms.ModelForm):
    class Meta:
        model = StoreList
        fields = {'statusstore', 'zone', 'status', 'serial', 'info'}
        labels = {'statusstore': 'نوع قطعه',
                  'zone': 'منطقه / کارگاه',
                  'status': 'وضعیت قطعه',
                  'serial': 'شماره سریال',
                  'info': 'توضیحات',
                  }


class RepqiresAddForm(forms.ModelForm):
    class Meta:
        model = Repaires
        fields = ['zone',]


class UploadAddForm(forms.ModelForm):
    class Meta:
        model = Repaires
        fields = ['marsole',]


class RepqiresAddStoreForm(forms.ModelForm):
    class Meta:
        model = RepaireStores
        fields = ['repairstore', 'amount']

class RepqireAddStoreName(forms.ModelForm):
    class Meta:
        model = RepairStoreName
        fields = ['name',]

class RepairParametrForm(forms.ModelForm):
    class Meta:
        model = RepairRole
        fields = ['minvalue','usevalue','startvalue']

