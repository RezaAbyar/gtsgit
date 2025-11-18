from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserPermission, DefaultPermission
from django.core.cache import cache
from django.conf import settings
import redis

rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, password=settings.REDIS_PASS)


def cache_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            owner_id = request.user.owner.id  # یا هر owner_id دیگری
            formpermmision = rd.hgetall(owner_id)
            if formpermmision:
            # تبدیل داده‌های باینری به رشته
                formpermmision = {key.decode('utf-8'): value.decode('utf-8') for key, value in formpermmision.items()}
            else:
                print('end time')
                formpermmision = get_user_permissions(request.user)


            access_role = rd.hget(owner_id, permission_name)

            if access_role:
                access_role = access_role.decode('utf-8')  # تبدیل باینری به رشته
                # print(f"Access role for {permission_name}: {access_role}")
            else:
                # print('end time')
                formpermmision = get_user_permissions(request.user)
            # بررسی دسترسی بر اساس permission_name
            if permission_name != '0' and access_role == 'no':
                messages.warning(request, "شما دسترسی لازم را ندارید.")
                return redirect('base:home')  # تغییر به صفحه‌ی اصلی

            # افزودن formpermmision به context
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'context_data'):
                response.context_data['formpermmision'] = formpermmision
            return response
        return wrapper
    return decorator


def add_form_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
            if not owner_p.exists():
                owner_p = DefaultPermission.objects.filter(
                    role_id=request.user.owner.role_id,
                    semat_id=request.user.owner.refrence_id
                )
            formpermmision = {i.permission.name: i.accessrole.ename for i in owner_p}

            # بررسی دسترسی بر اساس permission_name
            if permission_name != '0' and formpermmision.get(permission_name) == 'no':
                messages.warning(request, "شما دسترسی لازم را ندارید.")
                return redirect('home_page')  # تغییر به صفحه‌ی اصلی

            # افزودن formpermmision به context
            response = view_func(request, *args, **kwargs)

            if hasattr(response, 'context_data'):
                response.context_data['formpermmision'] = formpermmision
            return response

        return wrapper

    return decorator


def get_user_permissions(user):
    owner_p = UserPermission.objects.filter(owner_id=user.owner.id)
    if not owner_p.exists():
        owner_p = DefaultPermission.objects.filter(
            role_id=user.owner.role_id,
            semat_id=user.owner.refrence_id
        )
    permissions = {i.permission.name: i.accessrole.ename for i in owner_p}
    for i in owner_p:
        rd.hsetnx(user.owner.id, i.permission.name, i.accessrole.ename)
    rd.expire(user.owner.id, 3600)
    return permissions