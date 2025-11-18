import django
from django.db import connections
from django.db.utils import OperationalError
import threading




def create_connection():

    try:
        # ایجاد اتصال به دیتابیس
        connection = connections['default']
        connection.ensure_connection()

        # اجرای یک کوئری ساده
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        print(f"اتصال موفقیت‌آمیز بود.")

    except OperationalError as e:
        print(f"خطا در اتصال: {e}")


# ایجاد 2000 اتصال به دیتابیس
threads = []
u=0
for i in range(2000):
    print(u)
    u+=1
    thread = threading.Thread(target=create_connection)
    threads.append(thread)
    thread.start()

# منتظر بمانید تا همه threads به پایان برسند
for thread in threads:
    thread.join()

print("تمام اتصالات تست شده‌اند.")