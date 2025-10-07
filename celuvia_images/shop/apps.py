from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        """
        Tells django to load signals.py for address creation if user added
        address at signuo.
        """
        import shop.signals
