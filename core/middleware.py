"""Qo'shimcha xavfsizlik sarlavhalari: CSP, Permissions-Policy."""
import secrets

CSP_TEMPLATE = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "script-src 'self' 'nonce-{nonce}'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: blob:; "
    "media-src 'self' blob:; "
    "connect-src 'self'; "
    "frame-src https://www.youtube.com https://www.youtube-nocookie.com https://player.vimeo.com; "
    "worker-src 'self' blob:; "
    "manifest-src 'self'"
)

PERMISSIONS_POLICY = (
    "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
    "magnetometer=(), microphone=(), payment=(), usb=()"
)


class SecurityHeadersMiddleware:
    """Har bir javobga CSP qo'shadi va inline skript uchun nonce beradi.

    Django admin o'zining inline skriptlaridan foydalangani uchun /admin/ ga
    CSP qo'yilmaydi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)

        response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        response.setdefault("X-Content-Type-Options", "nosniff")

        if request.path.startswith("/admin/"):
            return response
        if "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = CSP_TEMPLATE.format(nonce=request.csp_nonce)
        return response
