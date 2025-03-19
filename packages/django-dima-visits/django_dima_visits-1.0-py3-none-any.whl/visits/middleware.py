from .models import Visit
from django.utils.timezone import now

class VisitMiddleware:
    """
    Middleware for tracking visits to pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # ثبت بازدید در پایگاه داده
        if request.path != "/favicon.ico":  # جلوگیری از ثبت درخواست فاویکون
            Visit.objects.create(
                page_url=request.path,
                ip_address=request.META.get('REMOTE_ADDR'),
                visit_time=now()
            )

        return response
