from rest_framework.permissions import BasePermission
from rest_framework.metadata import BaseMetadata

from base.models import UserPermission, DefaultPermission, GsList, Ticket


class GSCreatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
        if owner_p.count() == 0:
            owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id)
        ua = owner_p.get(permission__name='gs')
        return ua.accessrole_id in [3, 4]


class CustomMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        return {
            "name": view.get_view_name()
        }


class ShowFailurePermission(BasePermission):
    pass


#     def has_object_permission(self, request, view, obj):
#         owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
#         if owner_p.count() == 0:
#             owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id)
#         ua = owner_p.get(permission__name='acroles')
#         return ua.accessrole_id not in [5]


class CloseTicketOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        gs = GsList.objects.filter(gs_id=obj.gs.id)
        ticket = Ticket.objects.get(id=obj.id)
        if ticket.status_id == 1:
            if ticket.usererja == request.user.owner.id:
                return True
            for item in gs:
                if request.user.owner.id == item.owner_id:
                    return True
        if request.user.owner.role.role in ['fani', 'test', 'zone', 'setad', 'mgr', 'area', 'gs', 'engin']:
            return True
        if request.user.owner.refrence_id == 8:
            return True


class OwnerCreatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
        if owner_p.count() == 0:
            owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id)
        ua = owner_p.get(permission__name='users')
        return ua.accessrole_id in [3, 4]
