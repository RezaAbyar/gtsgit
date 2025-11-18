import base64
import zlib
from django.shortcuts import redirect
import datetime
from accounts.models import Logs
from .exceptions import QRProcessingError


def process_qr_code(qr_data: str, owner_id: int) -> str:
    """Process QR code data and return parsed information"""
    try:
        # Decode and decompress QR data
        decoded = base64.b64decode(qr_data)
        decompressed = zlib.decompress(decoded).decode('utf-8')

        return decompressed

    except Exception as e:
        raise QRProcessingError(f"Error processing QR code: {str(e)}")


def handle_qr_scan(request, qr_data: str, owner_id: int, is_rpm=False, ticket_id=None):
    """Handle QR code scanning process"""
    from sell.services.data_saver import DataSaver
    from sell.services.qr_parser import QRParser

    try:
        # Parse QR data
        parser = QRParser()
        parsed_data = parser.parse_qr_data(qr_data)

        # Save data to database
        saver = DataSaver(owner_id, parsed_data)
        result = saver.save_all()
        # Handle RPM case
        if is_rpm and ticket_id:
            from ..models import Ticket, Workflow
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.closedate = datetime.now()
            ticket.status_id = 2
            ticket.save()

            Workflow.objects.create(
                ticket_id=ticket_id,
                user_id=request.user.id,
                description='بستن تیکت RPM توسط تکنسین',
                organization_id=1,
                failure_id=ticket.failure_id,
                lat=request.POST.get('lat'),
                lang=request.POST.get('long')
            )
            return redirect('base:closeTicket')

        return result

    except QRProcessingError as e:
        Logs.objects.create(
            parametr1='مشکل رمزنگاری در رمزینه',
            parametr2=qr_data,
            owner_id=owner_id
        )
        return redirect('sell:listsell')