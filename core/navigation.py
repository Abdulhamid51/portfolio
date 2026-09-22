"""Ichki sahifalardagi “Qaytish” havolasi."""
from django.utils.http import url_has_allowed_host_and_scheme


def back_link(request, fallback):
    """Foydalanuvchi kelgan sahifa (agar u shu saytdan bo'lsa), aks holda `fallback`.

    Tashqi saytdan kelgan havola hech qachon ishlatilmaydi — bu ochiq
    yo'naltirish (open redirect) xavfini yopadi.
    """
    referer = (request.META.get("HTTP_REFERER") or "").strip()
    if not referer:
        return fallback
    if not url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return fallback
    # Sahifaning o'ziga qaytarib yubormaylik
    if referer.split("?")[0].rstrip("/") == request.build_absolute_uri(request.path).rstrip("/"):
        return fallback
    return referer
