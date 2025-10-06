from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User  # or your User model
from .models import Address


def create_user_address(sender, intance, created, **kwargs):
    """
    Automatically creates an address for the user in the shop app after they
    fill in the address details on signup. Is also set to the default for
    default address, shipping address and billing address.
    """
    if created:
        if instance.address_1 or i
