from django.core.management.base import BaseCommand
from base.models import Owner


class Command(BaseCommand):
    help = 'Update childcount for all owners'

    def handle(self, *args, **options):
        owners = Owner.objects.all()
        for owner in owners:
            owner.childcount = owner.calculate_child_count()
            owner.save(update_fields=['childcount'])
        self.stdout.write(self.style.SUCCESS('Successfully updated childcount for all owners'))
