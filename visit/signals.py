from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Certificate, CertificateAlert
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=Certificate)
def create_certificate_alerts(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'certificatealert'):
        # ایجاد هشدار 30 روز قبل از انقضا
        alert_date = instance.expiry_date - timezone.timedelta(days=30)
        CertificateAlert.objects.create(
            certificate=instance,
            alert_date=alert_date,
            message=f"گواهی {instance.certificate_type.name} جایگاه {instance.gs.name} در تاریخ {instance.expiry_date} منقضی می‌شود."
        )