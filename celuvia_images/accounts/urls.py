from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.buyer_signup, name="signup_buyer"),
    path("signup/vendor/", views.vendor_signup, name="signup_vendor"),
    path("login/", views.custom_login, name="login"),
]
