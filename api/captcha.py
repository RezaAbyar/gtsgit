from django.http import HttpResponse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import redis
from django.conf import settings


def generate_captcha_image(text):
    image = Image.new('RGB', (150, 40), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # اضافه کردن نویز به تصویر
    for _ in range(50):  # افزایش تعداد نقاط
        x = random.randint(0, 150)
        y = random.randint(0, 40)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    x_offset = 10
    for char in text:
        # ایجاد یک تصویر موقت برای هر کاراکتر
        char_image = Image.new('RGBA', (30, 30), (255, 255, 255, 0))
        text_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((0, 0), char, fill=text_color, font=font)

        # چرخش تصویر کاراکتر
        angle = random.randint(-10, 10)
        char_image = char_image.rotate(angle, expand=1)

        # قرار دادن کاراکتر چرخیده روی تصویر اصلی
        image.paste(char_image, (x_offset, 10), char_image)
        x_offset += 25  # فاصله بین کاراکترها

    for _ in range(2):
        x1 = random.randint(0, 150)
        y1 = random.randint(0, 40)
        x2 = random.randint(0, 150)
        y2 = random.randint(0, 40)
        draw.line((x1, y1, x2, y2), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def captcha_view(request):
    if not request.session.session_key:
        request.session.create()
    # تولید یک عدد تصادفی ۴ رقمی
    captcha_text = str(random.randint(10000, 99999))
    rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                     password=settings.REDIS_PASS)
    rd.setex(
        f"captcha:{request.session.session_key}",
        60,  #
        captcha_text
    )
    # ذخیره عدد در session برای بررسی بعدی
    request.session['captcha_text'] = captcha_text

    # تولید تصویر کپچا
    image_data = generate_captcha_image(captcha_text)

    # بازگرداندن تصویر به عنوان پاسخ HTTP
    return HttpResponse(image_data, content_type="image/png")
