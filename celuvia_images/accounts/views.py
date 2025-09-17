from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from .forms import BuyerSignUpForm, VendorSignUpForm


def buyer_signup(request):
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
