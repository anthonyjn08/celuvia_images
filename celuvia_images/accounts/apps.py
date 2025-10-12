from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    App configuration for the accounts app.
    Sets the app name and default ID field type.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
