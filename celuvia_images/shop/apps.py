from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Tells django to load signals.py for address creation if user added
    address at signuo. This will also allow the delivery address to
    prepoulate at checkout.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        import shop.signals
