import re

from django.db.models import Count

from pay.models import StoreList, StoreHistory


# تابع برای تبدیل اعداد فارسی به انگلیسی
def convert_persian_to_english_digits(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian_digit, english_digit in persian_to_english.items():
        text = text.replace(persian_digit, english_digit)
    return text


def clean_serials():
    i=0
    _a=(len(StoreList.objects.all()))
    for store in StoreList.objects.all():
        i+=1

        asseial =store.serial
        # تبدیل اعداد فارسی به انگلیسی
        cleaned_serial = convert_persian_to_english_digits(store.serial)
        # حذف خط فاصله و اسپیس
        cleaned_serial = re.sub(r'[- ]', '', cleaned_serial)
        # بررسی اینکه فقط شامل اعداد انگلیسی باشد
        if re.match(r'^[0-9]+$', cleaned_serial):
            print(f"{_a} / {i}شماره سریال  از {asseial}اصلاح شد: {store.serial}")
            try:
                store.serial = cleaned_serial
                store.save()
            except:
                print(f"{_a} / {i}شماره سریال  تکراری شد: {store.serial}")
                store.serial = f"{cleaned_serial}_9000"
                store.save()
        else:
            print(f"شماره سریال نامعتبر: {store.serial} (پس از اصلاح: {cleaned_serial})")



def fix_duplicate_serials():
    serial_counts = StoreList.objects.values('serial').annotate(count=Count('serial')).filter(count__gt=1)
    print(serial_counts)
    for item in serial_counts:
        serial = item['serial']
        duplicates = StoreList.objects.filter(serial=serial)
        for index, record in enumerate(duplicates[1:], start=1):  # از دومین رکورد شروع کنید
            new_serial = f"{serial}_{index}"
            while StoreList.objects.filter(serial=new_serial).exists():
                index += 1
                new_serial = f"{serial}_{index}"
            record.serial = new_serial
            record.save()
            print(f"شماره سریال {serial} به {new_serial} تغییر کرد.")


from django.core.management.base import BaseCommand



def adddate():

    store_list = StoreList.objects.all()

    for store in store_list:
        # Get the last StoreHistory record for this store
        last_history = StoreHistory.objects.filter(store=store).order_by('-create').first()

        if last_history:
            # Update the update field of StoreList with the create field of last_history
            store.update_date = last_history.create
            store.save()

    print('end')