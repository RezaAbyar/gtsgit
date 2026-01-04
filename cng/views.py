from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import CNGStation, Equipment, StationMeter, EquipmentSupplier, Capacity
from .forms import CNGStationForm, EquipmentForm, StationMeterForm
from base.models import Area,Zone,City
from django.db import models

# لیست جایگاه‌ها
class StationListView(LoginRequiredMixin, ListView):
    model = CNGStation
    template_name = 'cng/station_list.html'
    context_object_name = 'stations'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # فیلتر بر اساس منطقه
        zone_id = self.request.GET.get('zone')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)

        # جستجو
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(code__icontains=search) |
                models.Q(address__icontains=search)
            )

        return queryset.select_related('zone', 'area', 'city')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Zone.objects.all()
        return context


# جزئیات جایگاه
class StationDetailView(LoginRequiredMixin, DetailView):
    model = CNGStation
    template_name = 'cng/station_detail.html'
    context_object_name = 'station'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'action' in request.POST and request.POST['action'] == 'add_meter':
            meter_number = request.POST.get('meter_number')
            fee_type = request.POST.get('fee_type')

            if meter_number and fee_type:
                StationMeter.objects.create(
                    station=self.object,
                    meter_number=meter_number,
                    fee_type=int(fee_type)
                )
                messages.success(request, 'میتر جدید با موفقیت اضافه شد.')

        return redirect('cng:station_detail', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipments'] = self.object.equipments.all()
        context['meters'] = self.object.meters.all()
        return context


# ایجاد جایگاه جدید
class StationCreateView(LoginRequiredMixin, CreateView):
    model = CNGStation
    form_class = CNGStationForm
    template_name = 'cng/station_form.html'
    success_url = reverse_lazy('cng:station_list')

    def form_valid(self, form):
        messages.success(self.request, 'جایگاه جدید با موفقیت ایجاد شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f'{form.errors}خطایی رخ داده ')
        return super().form_invalid(form)


# ویرایش جایگاه
class StationUpdateView(LoginRequiredMixin, UpdateView):
    model = CNGStation
    form_class = CNGStationForm
    template_name = 'cng/station_form.html'

    def get_success_url(self):
        return reverse_lazy('cng:station_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'اطلاعات جایگاه با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


# حذف جایگاه
class StationDeleteView(LoginRequiredMixin, DeleteView):
    model = CNGStation
    template_name = 'cng/station_confirm_delete.html'
    success_url = reverse_lazy('cng:station_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'جایگاه با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)


# لیست تجهیزات یک جایگاه
class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'cng/equipment_list.html'
    context_object_name = 'equipments'
    paginate_by = 20

    def get_queryset(self):
        station_id = self.kwargs.get('station_id')
        if station_id:
            return Equipment.objects.filter(station_id=station_id)
        return Equipment.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station_id = self.kwargs.get('station_id')
        if station_id:
            context['station'] = get_object_or_404(CNGStation, pk=station_id)
        return context


# ایجاد تجهیز جدید
class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'cng/equipment_form.html'

    def dispatch(self, request, *args, **kwargs):
        # گرفتن station_id از URL و ذخیره آن
        self.station_id = kwargs.get('station_id')
        self.station = get_object_or_404(CNGStation, pk=self.station_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['station'] = self.station
        return context

    def get_success_url(self):
        return reverse_lazy('cng:equipment_list', kwargs={'station_id': self.station_id})

    def form_valid(self, form):
        # تنظیم station قبل از ذخیره
        form.instance.station = self.station
        messages.success(self.request, 'تجهیز جدید با موفقیت ایجاد شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'خطا در ایجاد تجهیز. لطفا اطلاعات را بررسی کنید.')
        return super().form_invalid(form)


# ویوهای مشابه برای StationMeter, EquipmentSupplier, Capacity

# AJAX View برای دریافت نواحی بر اساس منطقه
def get_areas_by_region(request):
    zone_id = request.GET.get('zone_id')
    areas = Area.objects.filter(zone_id=zone_id).order_by('name')
    return render(request, 'cng/area_options.html', {'areas': areas})


# AJAX View برای دریافت شهرها بر اساس ناحیه
def get_cities_by_area(request):
    area_id = request.GET.get('area_id')
    cities = City.objects.filter(area_id=area_id).order_by('name')
    return render(request, 'cng/city_options.html', {'cities': cities})



def meter_create(request, station_id):
    station = get_object_or_404(CNGStation, pk=station_id)

    if request.method == 'POST':
        form = StationMeterForm(request.POST)
        if form.is_valid():
            meter = form.save(commit=False)
            meter.station = station
            meter.save()
            messages.success(request, 'میتر با موفقیت ثبت شد.')
            return redirect('cng:station_detail', pk=station.pk)
    else:
        form = StationMeterForm()

    return render(request, 'cng/meter_form.html', {
        'form': form,
        'station': station,
        'title': 'ثبت میتر جدید'
    })