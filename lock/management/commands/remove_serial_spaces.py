from django.core.management.base import BaseCommand
from lock.models import LockModel
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Removes spaces from serial field in LockModel and handles duplicates'

    def handle(self, *args, **options):
        locks = LockModel.objects.all()
        total_updated = 0
        total_deleted = 0
        total_errors = 0

        for lock in locks:
            if ' ' in lock.serial:
                new_serial = lock.serial.replace(' ', '')

                # بررسی وجود سریال بدون فاصله
                if LockModel.objects.filter(serial=new_serial).exists():
                    try:
                        # حذف رکورد فعلی (با فاصله)
                        lock.delete()
                        total_deleted += 1
                        self.stdout.write(
                            self.style.WARNING(f'Deleted duplicate: {lock.serial} (duplicate of {new_serial})')
                        )
                    except Exception as e:
                        total_errors += 1
                        self.stdout.write(
                            self.style.ERROR(f'Error deleting {lock.serial}: {str(e)}')
                        )
                else:
                    try:
                        # آپدیت سریال بدون فاصله
                        old_serial = lock.serial
                        lock.serial = new_serial
                        lock.save()
                        total_updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated serial: {old_serial} -> {new_serial}')
                        )
                    except IntegrityError:
                        total_errors += 1
                        self.stdout.write(
                            self.style.ERROR(f'Duplicate found after update for: {new_serial}')
                        )
                    except Exception as e:
                        total_errors += 1
                        self.stdout.write(
                            self.style.ERROR(f'Error updating {lock.serial}: {str(e)}')
                        )

        # نمایش خلاصه عملیات
        self.stdout.write(self.style.SUCCESS('\nOperation Summary:'))
        self.stdout.write(self.style.SUCCESS(f'Total updated: {total_updated}'))
        self.stdout.write(self.style.WARNING(f'Total deleted (duplicates): {total_deleted}'))
        self.stdout.write(self.style.ERROR(f'Total errors: {total_errors}'))
        self.stdout.write(self.style.SUCCESS('Finished processing serial numbers'))