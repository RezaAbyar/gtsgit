# stations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from base.models import GsModel
from .models import PMChecklist
from .forms import PMChecklistForm

@login_required
def station_detail(request, pk):
    station = get_object_or_404(GsModel, pk=pk)
    checklists = station.checklists.all().order_by('-check_date')
    return render(request, 'station_detail.html', {
        'station': station,
        'checklists': checklists
    })

@login_required
def create_checklist(request, station_pk):
    station = get_object_or_404(GsModel, pk=station_pk)

    if request.method == 'POST':
        form = PMChecklistForm(request.POST, station=station)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.station = station
            checklist.technician = request.user
            checklist.save()
            messages.success(request, 'چک لیست با موفقیت ثبت شد.')
            return redirect('pm:station_detail', pk=station.pk)
    else:
        form = PMChecklistForm(station=station)

    return render(request, 'checklist_create.html', {
        'form': form,
        'station': station
    })

@login_required
def checklist_detail(request, pk):
    checklist = get_object_or_404(PMChecklist, pk=pk)
    return render(request, 'checklist_detail.html', {'checklist': checklist})