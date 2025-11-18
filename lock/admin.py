from django.contrib import admin

from .models import LockModel, Status, Seris, SendPoshtiban, Peymankar, Position, LockLogs, InsertLock


@admin.register(LockModel)
class LockModelAdmin(admin.ModelAdmin):
    list_display = ('zone', 'serial', 'status', 'ticket_id', 'meeting_number', 'ticket')
    list_filter = ['zone', 'status']
    list_editable = ('status',)
    search_fields = ['serial', 'gs__gsid']

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD', 'POST'):
            return False
        return super(LockModelAdmin, self).has_change_permission(request, obj)


@admin.register(InsertLock)
class InsertLockAdmin(admin.ModelAdmin):
    list_display = ('zone', 'serial_in', 'serial_out', 'tarikh', 'position')
    list_filter = ['zone']
    search_fields = ['serial_in', 'serial_out']


@admin.register(SendPoshtiban)
class SendPoshtibanAdmin(admin.ModelAdmin):
    list_display = ('zone', 'serial_in', 'serial_out', 'owner')
    list_filter = ['zone']
    search_fields = ['serial_in', 'serial_out']


@admin.register(LockLogs)
class LockLogsAdmin(admin.ModelAdmin):
    list_display = ('lockmodel', 'owner', 'status', 'gs', 'pump', 'position')
    list_filter = ['gs__area__zone']
    search_fields = ['gs']

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD', 'POST'):
            return False
        return super(LockLogsAdmin, self).has_change_permission(request, obj)


admin.site.register(Status)
admin.site.register(Seris)
admin.site.register(Peymankar)
admin.site.register(Position)
