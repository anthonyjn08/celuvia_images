from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class BuyerSignUpForm(UserCreationForm):
    """
    Sign up form for a buyers account.

    Fields:
        - first_name: CharField, users first name
        - last_name: CharField, users last name
        - email: EmailField, users email
        - phone_number: CharField, users phone number
        - address_1: CharField, first line of address
        - address_2: CharField, second line of address
        - town: CharField, address Town
        - city: CharField, address City
        - post_code: CharField, address post code
        - password1: CharField, password
        - password2: CharField, password
    """
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
            "phone_number", "address_1", "address_2",
            "town", "city", "post_code",
            "password1", "password2"
            ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "autofocus": True}),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}),
            "address_1": forms.TextInput(
                attrs={"class": "form-control"}),
            "address_2": forms.TextInput(
                attrs={"class": "form-control"}),
            "town": forms.TextInput(
                attrs={"class": "form-control"}),
            "city": forms.TextInput(
                attrs={"class": "form-control"}),
            "post_code": forms.TextInput(
                attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(
                attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control"}),
        }


class VendorSignUpForm(UserCreationForm):
    """
    Sign up form for a vendor account.

    Fields:
        - first_name: CharField, users first name
        - last_name: CharField, users last name
        - email: EmailField, users email
        - phone_number: CharField, users phone number
        - address_1: CharField, first line of address
        - address_2: CharField, second line of address
        - town: CharField, address Town
        - city: CharField, address City
        - post_code: CharField, address post code
        - password1: CharField, password
        - password2: CharField, password
    """
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
            "phone_number", "address_1", "address_2",
            "town", "city", "post_code",
            "password1", "password2"
            ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "autofocus": True}),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}),
            "address_1": forms.TextInput(
                attrs={"class": "form-control"}),
            "address_2": forms.TextInput(
                attrs={"class": "form-control"}),
            "town": forms.TextInput(
                attrs={"class": "form-control"}),
            "city": forms.TextInput(
                attrs={"class": "form-control"}),
            "post_code": forms.TextInput(
                attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(
                attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control"}),
        }


class LoginForm(forms.Form):
    """
    Login form.

    Fields:
        - email: EmailField, users email (username) address
        - password: CharField, users password
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control",
                                       "placeholder": "Email address"}),

        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control",
                                          "placeholder": "Password"}),

        label="Password",
    )
