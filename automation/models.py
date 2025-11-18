import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from base.models import Owner, Role,Zone,Area
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError


def tiff_upload_path(instance, filename):
    return f'tiff_files/{filename}'


def png_upload_path(instance, filename):
    return f'png_converted/{filename}'


class WordTemplate(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام قالب")
    template_file = models.FileField(
        upload_to='word_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="فایل قالب (DOCX)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Message(models.Model):

    def wrapper(instance, filename, ):
        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        filename = f"{unique_id}.{ext}"
        return os.path.join("automationfile/" + unique_id2, filename)

    def validate_image(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
            megabyte_limit = 500
            if filesize > megabyte_limit * 1024:
                raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        except:
            megabyte_limit = 500
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    sender = models.ForeignKey(Owner, related_name='sent_messages', on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Owner, related_name='received_messages')
    groups = models.ManyToManyField(Role, related_name='group_messages', blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(
        upload_to='message_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'])],
        help_text="فرمت‌های مجاز: JPG, JPEG, PNG, GIF, TIF, TIFF"
    )
    pdf_file = models.FileField(upload_to='topdf/', blank=True, null=True)
    is_converted = models.BooleanField(default=False)
    pages = models.IntegerField(default=1)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    sent_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)
    extracted_text = models.TextField(null=True, blank=True)
    files = models.FileField(upload_to=wrapper,validators=[validate_image], blank=True, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    is_draft = models.BooleanField(default=False, verbose_name="پیش‌نویس")
    word_file = models.FileField(
        upload_to='draft_word_files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="فایل ورد پیش‌نویس"
    )
    template = models.ForeignKey(
        WordTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="قالب نامه"
    )

    def __str__(self):
        return self.subject

    def convert_to_png(self):
        from PIL import Image
        png_pages = []

        # باز کردن فایل TIFF
        with Image.open(self.image) as img:
            # ذخیره هر صفحه به عنوان PNG
            for i in range(img.n_frames):
                img.seek(i)

                # ایجاد نام فایل
                original_name = os.path.splitext(os.path.basename(self.image.name))[0]
                png_name = f"{original_name}_page_{i + 1}.png"

                # تبدیل به PNG در حافظه
                output = BytesIO()
                img.save(output, format='PNG')
                output.seek(0)

                # ذخیره مدل PNG
                png_model = PngImage(
                    tiff_image=self,
                    page_number=i + 1
                )
                png_model.png_file.save(png_name, ContentFile(output.read()))
                png_pages.append(png_model)
                output.close()

        return png_pages

    def get_png_pages(self):
        """Get all converted PNG pages for this message"""
        if hasattr(self, 'png_pages'):
            return self.png_pages.all().order_by('page_number')
        return []

    def mark_as_read(self, user):
        self.read_at = timezone.now()
        self.save()
        # ثبت رویداد خواندن پیام
        MessageReadLog.objects.get_or_create(owner=user.owner, message=self)

    class Meta:
        ordering = ['-sent_at']


class PngImage(models.Model):
    tiff_image = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='png_pages')
    png_file = models.ImageField(upload_to=png_upload_path)
    page_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.tiff_image} - Page {self.page_number}"


class MessageReadLog(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='message_read_logs', blank=True, null=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_logs')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-read_at']
        unique_together = ['owner', 'message']  # هر کاربر فقط یک بار برای هر پیام لاگ می‌شود

    def __str__(self):
        return f"{self.owner.get_full_name()} read {self.message.subject} at {self.read_at}"


