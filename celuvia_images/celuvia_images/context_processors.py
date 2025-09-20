from django.conf import settings


def site_name(request):
    """
    Make SITE_NAME available in all templates.
    """
    return {"SITE_NAME": settings.SITE_NAME}


def categories(request):
    """
    import inside function to avoid app registry issues at import time
    """
    try:
        from shop.models import Category
        cats = Category.objects.all()
    except Exception:
        cats = []
    return {"categories": cats}
