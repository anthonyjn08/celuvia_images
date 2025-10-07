from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import Address


@receiver(post_save, sender=User)
def create_user_address(sender, instance, created, **kwargs):
    """
    Automatically creates an address for the user in the shop app after they
    fill in the address details on signup. Is also set to the default for
    default address, shipping address and billing address.
    """
    if created:
        if instance.address_1 or instance.city or instance.post_code:
            Address.objects.create(
                user=instance,
                full_name=instance.full_name,
                address_line1=instance.address_1,
                address_line2=instance.address_2,
                town=instance.town,
                city=instance.city,
                postcode=instance.post_code,
                phone=instance.phone_number,
                is_default=True,
                is_shipping=True,
                is_billing=True,
            )
