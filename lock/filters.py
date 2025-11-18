import django_filters
from django import forms
from .models import *
from base.models import Zone, Area, GsModel, Owner


class LockFilter(django_filters.FilterSet):
    zone = django_filters.ModelMultipleChoiceFilter(field_name='zone', queryset=Zone.objects_limit.all(),
                                                    widget=forms.SelectMultiple)
    area = django_filters.ModelMultipleChoiceFilter(field_name='gs__area', queryset=Area.objects.none(),
                                                    widget=forms.SelectMultiple)
    gs = django_filters.ModelMultipleChoiceFilter(field_name='gs', queryset=GsModel.objects.none(),
                                                  widget=forms.SelectMultiple)
    owner = django_filters.ModelMultipleChoiceFilter(field_name='owner', queryset=Owner.objects.none(),
                                                     widget=forms.SelectMultiple)
    # status = django_filters.ModelMultipleChoiceFilter(field_name='status',
    #                                                   queryset=Status.objects.filter(id__in=[3, 4, 5, 6, 9, 7, 11, 8]),
    #                                                   widget=forms.SelectMultiple)
    status = django_filters.ModelMultipleChoiceFilter(field_name='status',
                                                      queryset=Status.objects.all(),  # همه وضعیت‌ها
                                                      widget=forms.SelectMultiple)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(LockFilter, self).__init__(*args, **kwargs)

        # تنظیم queryset بر اساس request
        if request:
            if request.user.owner.role.role in ['tek', 'gs']:
                self.filters['zone'].queryset = Zone.objects.filter(id=request.user.owner.zone.id)
                self.filters['gs'].queryset = GsModel.objects.filter(gsowner__owner_id=request.user.owner.id)
                self.filters['owner'].queryset = Owner.objects.filter(id=request.user.owner.id)
            elif request.user.owner.role.role == 'zone':
                self.filters['zone'].queryset = Zone.objects.filter(id=request.user.owner.zone.id)
                self.filters['gs'].queryset = GsModel.objects.filter(area__zone_id=request.user.owner.zone.id)
                self.filters['owner'].queryset = Owner.objects.filter(zone_id=request.user.owner.zone.id,
                                                                      role__role='tek')
                self.filters['area'].queryset = Area.objects.filter(zone_id=request.user.owner.zone.id)
            elif request.user.owner.role.role == 'area':
                self.filters['zone'].queryset = Zone.objects.filter(id=request.user.owner.zone.id)
                self.filters['gs'].queryset = GsModel.objects.filter(area_id=request.user.owner.area.id)
