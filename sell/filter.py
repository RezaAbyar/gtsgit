import django_filters
from django import forms

from base.models import Zone,Product
from .models import *

class RepmgrFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='tarikh', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='tarikh', lookup_expr='lte')
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    product = django_filters.ModelMultipleChoiceFilter(field_name='product', queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)