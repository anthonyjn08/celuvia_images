from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.timezone import now
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Manager for CustomUser model.

    Provides helper methods to create regular users and superusers
    with email as the unique identifier instead of username.
    """
    def create_user(
            self, email, first_name, last_name, password=None, **extra_fields
            ):
        """
        Create and save a regular user using the enrtered email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a superuser using the enrtered email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(
            email, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for Buyers and Vendors.
    Uses email as the login field.

    Fields:
        - user_name: Populated using users first and last name.
        - first_name: CharField, users first name.
        - last_name: CharField, users last name.
        - email: EmailField, users email.
        - phone_number: CharField, users phone number.
        - address_1: CharField, first line of address.
        - address_2: CharField, second line of address.
        - town: CharField, address Town.
        - city: CharField, address City.
        - post_code: CharField, address post code.
        - password1: CharField, password.
        - password2: CharField, password.
    """
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address_1 = models.CharField(max_length=50, blank=True)
    address_2 = models.CharField(max_length=50, blank=True)
    town = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)

    def is_vendor(self):
        return self.groups.filter(name="Vendors").exists()

    def is_buyer(self):
        return self.groups.filter(name="Buyers").exists()


class ResetToken(models.Model):
    """
    Stores a password reset token for a user.

    Fields:
        - user: Foriegn key, the user requesting password reset.
        - token: CharField, the unique password token to verify the
          reset link.
        - expiry_date: DateTimeField, the date and time of the reset
          token expires.
        - used: BooleanField, sets whether the token has already been used.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and self.expiry_date > now()

    def __str__(self):
        return f"{self.user.email} - {self.token}"
