import json
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import Owner  # یا مسیر صحیح به مدل Owner


class UserDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f"user_data_{request.user.id}"
            cached_data = cache.get(cache_key)

            if cached_data:
                request.user_data = json.loads(cached_data)
            else:
                # اگر در کش نبود، از دیتابیس بخوان و در کش ذخیره کن
                request.user_data = self._get_user_data(request.user)

        return self.get_response(request)

    def _get_user_data(self, user):
        try:
            owner = Owner.objects.select_related('role', 'zone', 'area').get(user=user)

            user_data = {
                'owner_id': owner.id,
                'role_name': owner.role.role if owner.role else None,
                'role_id': owner.role.id if owner.role else None,
                'zone_id': owner.zone.id if owner.zone else None,
                'area_id': owner.area.id if owner.area else None,
                'full_name': owner.get_full_name(),
            }

            # ذخیره در کش
            cache_key = f"user_data_{user.id}"
            cache.set(cache_key, json.dumps(user_data), timeout=86400)  # 24 hours

            return user_data
        except Owner.DoesNotExist:
            return {}