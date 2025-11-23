from django.core.management.base import BaseCommand
from sell.models import QRScan
from sell.qrreader import load_code

class Command(BaseCommand):
    help = 'Update nerkh'

    def add_arguments(self, parser):
        parser.add_argument('Dore', type=int, help='Dore')

    def handle(self, *args, **options):
        dore = options['Dore']
        for batch in QRScan.objects.filter(dore=dore):
            load_code(
                f'1:1:{batch.qr_data1}',
                batch.owner.id)

        self.stdout.write(self.style.SUCCESS('Successfully Delete All Locks'))
