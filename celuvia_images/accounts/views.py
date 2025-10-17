import secrets
from hashlib import sha1
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import ResetToken
from .forms import BuyerSignUpForm, VendorSignUpForm, LoginForm
from shop.models import Store, Category, Product

User = get_user_model()


def groups_and_permissions():
    """
    This function is used to check whether the Buyer and Vendor users groups
    exist in the database, with the required permissions. If they do not exist
    then the group will be created with the permissions.
    """
    # Create Buyers group
    buyers_group, created = Group.objects.get_or_create(name="Buyers")

    # Create Vendors group
    vendors_group, created = Group.objects.get_or_create(name="Vendors")

    # Select models to grant permissions for
    shop_models = [Category, Product, Store]
    vendor_permissions = []

    for model in shop_models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                f"add_{model._meta.model_name}",
                f"change_{model._meta.model_name}",
                f"view_{model._meta.model_name}",
            ],
        )
        vendor_permissions.extend(permissions)

    # Add the created permissions to the Vendr group if needed
    for permission in vendor_permissions:
        vendors_group.permissions.add(permission)

    return buyers_group, vendors_group


def buyer_signup(request):
    """
    Allows new users to signup as a buyer. If the Buyers group foesn't exist,
    it will be created and the user assigned to the buyers group. If the group
    already exists, new users will be assigned.

    - param request: HTTP request object.
    - return: Redirect to home on successful signup, or rendered buyer
      signup form on GET.
    """
    if request.method == "POST":
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()

            # Check the user group exists
            buyers_group, created = Group.objects.get_or_create(name="Buyers")
            user.groups.add(buyers_group)
            login(request, user)
            messages.success(
                request, "Your account has been created successfully!")

            return redirect("shop:home")
    else:
        form = BuyerSignUpForm()
    return render(request, "accounts/signup_buyer.html", {"form": form})


def vendor_signup(request):
    """
    Allows new users to signup as a vendor and sell products. If the Vendors
    user group does not already exist, The user group will be created, have
    the required permissions added, and then assign the user to the group.
    If the group and permissions exist, users will be added.

    - param request: HTTP request object.
    - return: Redirect to vendor dashboard on successful signup, or
      rendered vendor signup form on GET.
    """
    if request.method == "POST":
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()

            # Check if the vendor group exists or needs to be created
            vendors_group, buyers_group = groups_and_permissions()

            # Assign the user
            user.groups.add(vendors_group, buyers_group)
            login(request, user)
            messages.success(request,
                             "Your account has been created successfully!")
            return redirect("shop:vendor_dashboard")
    else:
        form = VendorSignUpForm()
    return render(request, "accounts/signup_vendor.html", {"form": form})


def login_view(request):
    """
    Handle user login.

    - param request: HTTP request object.
    - return: redirect to home if login successful, or rendered login
      form template on GET or failed login.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Logged in successfully.")
                    return redirect("shop:home")
                else:
                    messages.error(request, "This account is inactive.")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """
    Handle user logout and direct them back to the homepage.

    - param request: HTTP request object.
    - return: redirect to home page after logout.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("shop:home")


def request_password_reset(request):
    """
    Handle password reset request.

    - param request: HTTP request object.
    - return: rendered confirmation template after POST, or password
      reset request form on GET.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            # Generate secure token
            token_str = secrets.token_urlsafe(16)
            token_hash = sha1(token_str.encode()).hexdigest()
            expiry_date = now() + timedelta(minutes=10)

            ResetToken.objects.create(
                user=user,
                token=token_hash,
                expiry_date=expiry_date,
            )

            reset_url = request.build_absolute_uri(
                reverse("accounts:reset_password", args=[token_str])
            )

            # Send email
            subject = "Password Reset Request"
            body = (f"Hi {user.full_name},\n\nUse the link below to reset "
                    f"your password:\n{reset_url}\n\nThis link will expire "
                    f"in 10 minutes.")
            email_msg = EmailMessage(subject, body, "noreply@celuvia.com",
                                     [user.email])
            email_msg.send()

        return render(request, "accounts/reset_requested.html")

    return render(request, "accounts/request_password_reset.html")


def reset_password(request, token):
    """
    Handles users password reset via the reset token.

    - param request: HTTP request object.
    - param token: unique token used to validate password reset request.
    - return: redirect to login on success, rendered reset form on GET,
      or invalid token template if expired or invalid.
    """
    token_hash = sha1(token.encode()).hexdigest()
    try:
        reset_token = ResetToken.objects.get(token=token_hash, used=False)
    except ResetToken.DoesNotExist:
        reset_token = None

    if not reset_token or reset_token.expiry_date < now():
        if reset_token:
            reset_token.delete()
        return render(request, "accounts/reset_invalid.html")

    if request.method == "POST":
        password = request.POST.get("password")
        password_conf = request.POST.get("password_conf")
        if password == password_conf:
            reset_token.user.set_password(password)
            reset_token.user.save()
            reset_token.used = True
            reset_token.save()
            messages.success(request,
                             "Your password has been reset. Please log in.")
            return HttpResponseRedirect(reverse("accounts:login"))
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "accounts/reset_password.html", {"token": token})
