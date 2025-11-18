from rest_framework.permissions import BasePermission

from user.models import GroupBank


class IsPT(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.contains(GroupBank.pt)


class IsTradeSystem(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.contains(GroupBank.trade_system)


class IsMonitoring(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.contains(GroupBank.monitoring)
