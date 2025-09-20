import secrets
from hashlib import sha1
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import BuyerSignUpForm, VendorSignUpForm
from .models import ResetToken

User = get_user_model()


def buyer_signup(request):
    """
    Buyer signup.

    - param request: HTTP request object.
    - return: Rendered template of products.
    """
    if request.method == "POST":
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name="Buyers")
            user.groups.add(group)
            login(request, user)
            messages.success(
                request, "Your account has been created successfully!")

            return redirect("shop:product_list")
    else:
        form = BuyerSignUpForm()
    return render(request, "accounts/signup_buyer.html", {"form": form})


def vendor_signup(request):
    """
    Vendor signup.

    - param request: HTTP request object.
    - return: Rendered template of vendor dashboard.
    """
    if request.method == "POST":
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name="Vendors")
            user.groups.add(group)
            messages.success(request,
                             "Your account has been created successfully!")
            return redirect("shop:vendor_dashboard")
    else:
        form = VendorSignUpForm()
    return render(request, "accounts/signup_vendor.html", {"form": form})


def custom_login(request):
    """
    Login view.

    - param request: HTTP request object.
    - return: Rendered template of vendor dashboard.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("shop:product_list")
        return render(
            request, "accounts/login.html", {"error": "Invalid credentials"})
    return render(request, "accounts/login.html")


def request_password_reset(request):
    """
    View for users to request a password reset email.
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
    Password reset.
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
            return HttpResponseRedirect(reverse("accounts:login"))

    return render(request, "accounts/reset_password.html",
                  {"token": token})
