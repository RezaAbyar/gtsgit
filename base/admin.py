from django.contrib import admin
from .models import *


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'areaid')
    list_editable = ('areaid',)
    list_filter = ['zone']


class ZoneAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'tekcount', 'storage', 'iscoding', 'ticket_benzin', 'ticket_super', 'ticket_gaz', 'bypass_sell',
        'issejelli', 'showdashboard')
    list_editable = (
        'tekcount', 'storage', 'iscoding', 'ticket_benzin', 'ticket_super', 'ticket_gaz', 'bypass_sell', 'issejelli',
        'showdashboard')


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('info', 'name', 'isrole', 'Sortper', 'permit', 'cat_sort')
    list_editable = ('permit', 'cat_sort')
    list_filter = ['Sortper']


class RefrenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'showlevel', 'ename')
    list_editable = ('showlevel', 'ename')


class OwnerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'lname', 'codemeli', 'mobail', 'role', 'daghimande', 'isboarder', 'mobail_ischeck', 'active')
    list_editable = ('daghimande',)
    list_filter = ['zone', 'role']
    search_fields = ['codemeli', ]


class GsListAdmin(admin.ModelAdmin):
    list_display = ('owner', 'gs')


class GsModelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'area', 'gsid', 'sellcode', 'btmt', 'isazadforsell', 'isqrcode', 'issell', 'iscoding', 'iszonetable',
        'status',
        'nazel_samane', 'addsell')
    list_filter = ['area__zone', ]
    list_editable = ('addsell', 'isazadforsell', 'isqrcode',)
    search_fields = ['gsid', 'sellcode']


class PumpAdmin(admin.ModelAdmin):
    list_display = ('gs', 'sakoo', 'tolombe', 'number', 'product')
    list_filter = ['gs__area__zone', ]
    search_fields = ['gs__gsid', ]


class DPAdmin(admin.ModelAdmin):
    list_display = ('role', 'accessrole', 'permission')
    list_filter = ['permission', ]


class UPAdmin(admin.ModelAdmin):
    list_display = ('owner', 'accessrole', 'permission')
    list_filter = ['permission', 'owner']


class SubAdmin(admin.ModelAdmin):
    list_display = (
        'failurecategory', 'info', 'organization', 'level', 'isnazel', 'isclosetek', 'organizationclose', 'editable')
    list_editable = ('isnazel', 'isclosetek', 'organizationclose', 'editable')
    list_filter = ['failurecategory', ]


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'pdate', 'failure', 'gs', 'status', 'organization', 'Pump', 'isdaghi', 'serialmaster', 'serialpinpad',
        'temp', 'humidity', 'main')
    search_fields = ['id', 'gs__gsid']
    list_filter = ['gs__area__zone', 'organization', 'failure', 'status']
    list_editable = ('status', 'organization', 'isdaghi', 'failure')

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD', 'POST'):
            return False
        return super(TicketAdmin, self).has_change_permission(request, obj)

    # def has_delete_permission(self, request, obj=None):
    #     return False


class WorkflowAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ticket', 'createdate', 'organization', 'description', 'failure', 'lat', 'lang', 'serialmaster',
        'serialpinpad')
    search_fields = ['ticket']
    list_filter = ['ticket__gs__area__zone', ]
    list_editable = ('organization', 'failure', 'serialmaster', 'serialpinpad')

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD', 'POST'):
            return False
        return super(WorkflowAdmin, self).has_change_permission(request, obj)

    # def has_delete_permission(self, request, obj=None):
    #     return False


class ReplyAdmin(admin.ModelAdmin):
    list_display = (
        'info', 'changemaster', 'changepinpad', 'organization', 'sort_id', 'forwarditem', 'isdaghimaster',
        'isdaghipinpad',
        'nocloseafteraccept', 'ispeykarbandi')
    list_filter = ['organization', ]
    list_editable = (
        'changemaster', 'changepinpad', 'isdaghimaster', 'isdaghipinpad', 'nocloseafteraccept', 'ispeykarbandi')


class TicketScienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'gs', 'status', 'amount', 'create', 'pump', 'information')
    search_fields = ['gs__gsid']


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'area')
    list_filter = ['area', ]


class CloseGSAdmin(admin.ModelAdmin):
    list_display = ('id', 'gs', 'date_in', 'date_out')
    search_fields = ['gs__gsid']


class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zone', 'iszarib', 'zarib', 'level', 'active', 'sortid', 'refrence')
    list_editable = ('level', 'active', 'sortid')


class AutoExcelAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'status', 'newstatus', 'errorstatus', 'reportmodel', 'created', 'started', 'ended')


class OwnerZoneAdmin(admin.ModelAdmin):
    list_display = ('owner', 'zone',)
    autocomplete_fields = ('owner',)


class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'sort',)


class TaskLogAdmin(admin.ModelAdmin):
    list_display = (
        'task_id', 'info', 'created', 'updated')


class MountAdmin(admin.ModelAdmin):
    list_display = (
        'mount', 'year', 'mah', 'day', 'active', 'isshow')


class PeykarbandylogAdmin(admin.ModelAdmin):
    list_display = ('gs', 'nazel', 'owner', 'created_at', 'code')
    search_fields = ['gs__gsid']


admin.site.register(TicketScience, TicketScienceAdmin),
admin.site.register(Ipc),
admin.site.register(Status),
admin.site.register(Modem),
admin.site.register(Rack),
admin.site.register(Printer),
admin.site.register(ThinClient),
admin.site.register(Refrence, RefrenceAdmin)
admin.site.register(Product)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Role)
admin.site.register(Area, AreaAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(GsModel, GsModelAdmin)
admin.site.register(GsList, GsListAdmin)
admin.site.register(PumpBrand)
admin.site.register(Pump, PumpAdmin)
admin.site.register(Organization)
admin.site.register(FailureCategory)
admin.site.register(FailureSub, SubAdmin)
admin.site.register(StatusTicket)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(AccessList)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(DefaultPermission, DPAdmin)
admin.site.register(UserPermission, UPAdmin)
admin.site.register(AccessRole)
admin.site.register(Mount, MountAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(Education)
admin.site.register(Operator)
admin.site.register(Parametrs)
admin.site.register(StatusMoavagh)
admin.site.register(CloseGS, CloseGSAdmin)
admin.site.register(Scores)
admin.site.register(NegativeScore)
admin.site.register(FilesSubject)
admin.site.register(GsStatus)
admin.site.register(AutoExcel, AutoExcelAdmin)
admin.site.register(OwnerZone, OwnerZoneAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(TaskLogs, TaskLogAdmin)
admin.site.register(ReInitial)
admin.site.register(Statuspump)
admin.site.register(Brand)
admin.site.register(CompanyStatus)
admin.site.register(Company)
admin.site.register(NewSejelli)
admin.site.register(LoginInfo)
admin.site.register(RequiredFieldsConfig)
admin.site.register(City, CityAdmin)
admin.site.register(Peykarbandylog, PeykarbandylogAdmin)
