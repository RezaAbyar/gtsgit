import django_filters
from django import forms
from .models import *
from base.models import Zone, Area



class CardFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)

    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)

    gs = django_filters.ModelMultipleChoiceFilter(field_name='gs', queryset=GsModel.objects.all(),
                                                  widget=forms.SelectMultiple)

    status = django_filters.ModelMultipleChoiceFilter(field_name='statuspan', queryset=StatusPan.objects.all(),
                                                      widget=forms.SelectMultiple)


class CardFilterZone(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)

    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)

    gs = django_filters.ModelMultipleChoiceFilter(field_name='gs', queryset=GsModel.objects.all(),
                                                  widget=forms.SelectMultiple)

    status = django_filters.ModelMultipleChoiceFilter(field_name='statuspan', queryset=StatusPan.objects.all(),
                                                      widget=forms.SelectMultiple)


class AzadFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='gs__area__zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)

    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.all(),
                                                    widget=forms.SelectMultiple)

    gs = django_filters.ModelMultipleChoiceFilter(field_name='gs', queryset=GsModel.objects.all(),
                                                  widget=forms.SelectMultiple)

    status = django_filters.ModelMultipleChoiceFilter(field_name='status', queryset=StatusCardAzad.objects.all(),
                                                      widget=forms.SelectMultiple)
    product = django_filters.ModelMultipleChoiceFilter(field_name='product', queryset=Product.objects.all(),
                                                       widget=forms.SelectMultiple)
