from django.contrib.auth import get_user_model
from django.http import HttpResponseServerError
from functools import wraps
from accounts.models import Logs

class QRProcessingError(Exception):
    """Base exception for QR processing errors"""

    pass


class QRParsingError(QRProcessingError):

    """Exception for QR data parsing errors"""
    pass


class DataSavingError(QRProcessingError):

    """Exception for data saving errors"""
    pass


def log_error(error_message: str, additional_data: str = "",
              owner=None, gs_id=None, request=None):
    """
    Helper function to log errors to Logs model
    """
    try:
        # Get owner from request if available
        if request and request.user.is_authenticated:
            owner = request.user.owner

        # Create log entry
        Logs.objects.create(
            owner=owner,
            parametr1=error_message[:2000],  # Truncate if too long
            parametr2=additional_data[:2000],
            gs=gs_id,
            macaddress=getattr(request, 'META', {}).get('REMOTE_ADDR', '0')
        )
    except Exception as e:
        # Fallback in case logging fails
        print(f"Failed to log error: {e}")

def handle_qr_errors(log_to_db=True):
    """
    Decorator to handle QR processing errors and log them
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except QRProcessingError as e:
                if log_to_db:
                    log_error(
                        f"QR Processing Error: {str(e)}",
                        f"Request path: {request.path}",
                        request=request,
                        gs_id=kwargs.get('gs_id')
                    )
                # You can return a custom response here
                return HttpResponseServerError("Error processing QR code")
            except Exception as e:
                if log_to_db:
                    log_error(
                        f"Unexpected Error: {str(e)}",
                        f"Request path: {request.path}",
                        request=request,
                        gs_id=kwargs.get('gs_id')
                    )
                raise  # Re-raise unexpected errors
        return wrapper
    return decorator