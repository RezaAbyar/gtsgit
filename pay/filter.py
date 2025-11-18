import django_filters
from django import forms
from openpyxl.descriptors import Max

from pay.models import StatusRef
from .models import *

class RepaireFilters(django_filters.FilterSet):


    zone = django_filters.ModelMultipleChoiceFilter(field_name='area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
