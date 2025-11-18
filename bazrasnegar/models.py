import os
from django.db import models
from django.utils.crypto import get_random_string
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def tiff_upload_path(instance, filename):
    return f'tiff_files/{filename}'

def png_upload_path(instance, filename):
    return f'png_converted/{filename}'

class BazrasNegar(models.Model):
    def wrapper(instance, filename, ):

        ext = filename.split(".")[-1].lower()
        unique_id = get_random_string(length=32)
        unique_id2 = get_random_string(length=32)
        filename = f"{unique_id}.{ext}"
        return os.path.join("bazrasi/" + unique_id2, filename)

    number = models.CharField(max_length=20, null=True, blank=True)
    tarikh = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=wrapper, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    extracted_text = models.TextField(null=True, blank=True)

    def convert_to_png(self):
        from PIL import Image
        png_pages = []

        # باز کردن فایل TIFF
        with Image.open(self.file) as img:
            # ذخیره هر صفحه به عنوان PNG
            for i in range(img.n_frames):
                img.seek(i)

                # ایجاد نام فایل
                original_name = os.path.splitext(os.path.basename(self.file.name))[0]
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

    def __str__(self):
        return self.title


class PngImage(models.Model):
    tiff_image = models.ForeignKey(BazrasNegar, on_delete=models.CASCADE, related_name='png_pages')
    png_file = models.ImageField(upload_to=png_upload_path)
    page_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.tiff_image} - Page {self.page_number}"
