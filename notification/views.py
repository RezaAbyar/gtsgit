"""pip install pywebpush"""
from django.views.decorators.csrf import csrf_exempt
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import PushSubscription, Notification
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

@csrf_exempt
def save_subscription(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            subscription = PushSubscription(
                user=request.user,  # یا هر کاربری که می‌خواهید
                endpoint=data['endpoint'],
                keys=data['keys']
            )
            subscription.save()
        except:
           pass
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def send_web_push_notification(user, title, message):
    subscriptions = PushSubscription.objects.filter(user=user)
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": subscription.keys
                },
                data=json.dumps({"title": title, "body": message}),
                vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
                vapid_claims={
                    "sub": f"mailto:{settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']}"
                }
            )
            print("VAPID_PRIVATE_KEY", subscription.user)
        except WebPushException as ex:
            print("WebPush failed: ", ex)


def notify_all_users(request):
    users = User.objects.all()
    msg = Notification.objects.filter(active=True).last()

    for user in users:
        send_web_push_notification(user, msg.subject, msg.info)
    return JsonResponse({'status': 'success'})