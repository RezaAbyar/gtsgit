from django.core.management.base import BaseCommand
from lock.models import LockModel


class Command(BaseCommand):
    help = 'Delete All Locks For Zone'

    def add_arguments(self, parser):
        parser.add_argument('Zone_id', type=int, help='Zone id to filter Locks')

    def handle(self, *args, **options):
        zone_id = options['Zone_id']
        LockModel.objects.filter(zone_id=zone_id).delete()
        self.stdout.write(self.style.SUCCESS('Successfully Delete All Locks'))
