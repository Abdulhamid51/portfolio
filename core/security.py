"""Kichik himoya yordamchilari: IP aniqlash va urinishlar chegarasi."""
import hashlib

from django.core.cache import cache


def client_ip(request):
    """Proksi ortida ham to'g'ri IP (faqat birinchi manzil olinadi)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:45]
    return request.META.get("REMOTE_ADDR", "") or "nomalum"


def _key(prefix, value):
    digest = hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:24]
    return f"throttle:{prefix}:{digest}"


def too_many(prefix, value, limit, window):
    """Chegaradan oshgan bo'lsa True qaytaradi (hisobni oshirmaydi)."""
    return cache.get(_key(prefix, value), 0) >= limit


def record_attempt(prefix, value, window):
    """Bitta urinishni belgilaydi va jami sonini qaytaradi."""
    key = _key(prefix, value)
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, window)
        return 1


def reset_attempts(prefix, value):
    cache.delete(_key(prefix, value))
