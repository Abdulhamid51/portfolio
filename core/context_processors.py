from django.utils import timezone

from .models import Profile, SocialLink


def site_context(request):
    """Har bir sahifada kerak bo'ladigan umumiy ma'lumotlar."""
    profile = Profile.load()
    return {
        "profile": profile,
        "social_links": SocialLink.objects.all(),
        "today": timezone.localdate(),
        "can_edit": request.user.is_authenticated and request.user.is_active,
        "csp_nonce": getattr(request, "csp_nonce", ""),
    }
