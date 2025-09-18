from django.conf import settings

def site_name(request):
    """Make SITE_NAME available in all templates."""
    return {"SITE_NAME": settings.SITE_NAME}
