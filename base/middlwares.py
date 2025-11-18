from django.shortcuts import redirect
from django.contrib import messages
from base.models import DefaultPermission, UserPermission
from accounts.models import Visits
import threading

LOGIN_EXEMPT_URLS = [
    '/login/',
    '/media/loginimage/',  # اضافه کردن این خط برای دسترسی به فایل‌های رسانه
    '/captcha/',
    '/veryfi/',
    '/accounts/recover_password/',
    '/cart/SearchCard/',
    '/api/captcha/',
    '/api/get-gs-info-btmt/',
    '/api/set-gs-ispay-btmt/',
    '/api/get-send-sms/',
    '/api/get-sell-info/',
    '/api/get-sell-info-all/',
    '/api/get-gs-location/',
    '/api/waybill/',
    '/api/gs-by-area/',
    '/api/get-gs-start_date/',
    '/accounts/api-token-auth/',
    '/cardapi/card-search/'
]

LOGIN2_EXEMPT_URLS = [
    '/login/',
    '/media/loginimage/',  # اضافه کردن این خط برای دسترسی به فایل‌های رسانه
]


class UserAccessMidlware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # اجازه دسترسی به فایل‌های رسانه بدون نیاز به احراز هویت
        if request.path.startswith('/media/loginimage/'):
            return self.get_response(request)


        elif not request.user.is_authenticated and request.path not in LOGIN_EXEMPT_URLS:
            result = str(request.path)
            return redirect('base:login')

        response = self.get_response(request)
        return response


class UserVisitMidlware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in LOGIN2_EXEMPT_URLS:
            ip = "0.0.0.0"
            if request.user.is_authenticated:
                user = request.user.username
                user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
                if user_ip:
                    ip = user_ip.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
            else:
                user = ""

        response = self.get_response(request)
        return response


class RequestMiddleware(object):
    def __init__(self, get_response, thread_local=threading.local()):
        self.get_response = get_response
        self.thread_local = thread_local

    def __call__(self, request):
        self.thread_local.current_request = request
        response = self.get_response(request)
        return response


class IsSecureMidlware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure():
            return redirect('base:login')
        return self.get_response(request)