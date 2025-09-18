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
            login(request, user)
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
            token = secrets.token_urlsafe(16)
            expiry = now() + timedelta(minutes=10)
            ResetToken.objects.create(
                user=user,
                token=sha1(token.encode()).hexdigest(),
                expiry_date=expiry
            )
            reset_url = request.build_absolute_uri(
                reverse("accounts:reset_password", args=[token])
            )

            subject = "Password Reset - Celuvia Images"
            body = f"Hi {user.full_name},\n\n"
            body += (f"Here is your password reset link (valid 10 minutes):"
                     f"\n{reset_url}\n\n")
            body += "If you did not request this, you can ignore this email."

            email_msg = EmailMessage(subject, body, to=[user.email])
            email_msg.send()

            return render(request, "accounts/password_reset_requested.html")
        except User.DoesNotExist:
            return render(request, "accounts/password_reset.html",
                          {"error": "No user with that email."})

    return render(request, "accounts/password_reset.html")


def reset_password(request, token):
    """
    Password reset.
    """
    hashed = sha1(token.encode()).hexdigest()
    try:
        reset_token = ResetToken.objects.get(token=hashed)
    except ResetToken.DoesNotExist:
        return render(request, "accounts/password_reset_invalid.html")

    if not reset_token.is_valid():
        reset_token.delete()
        return render(request, "accounts/password_reset_invalid.html")

    if request.method == "POST":
        password = request.POST.get("password")
        password_conf = request.POST.get("password_conf")
        if password and password == password_conf:
            user = reset_token.user
            user.set_password(password)
            user.save()
            reset_token.delete()
            return redirect("accounts:login")
        return render(request, "accounts/password_reset_confirm.html",
                      {"token": token, "error": "Passwords do not match"})

    return render(request, "accounts/password_reset_confirm.html",
                  {"token": token})
