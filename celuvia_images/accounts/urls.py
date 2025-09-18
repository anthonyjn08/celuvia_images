from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.buyer_signup, name="signup_buyer"),
    path("signup/vendor/", views.vendor_signup, name="signup_vendor"),
    path("login/", views.custom_login, name="login"),
    path("reset/", views.request_password_reset,
         name="password_reset_request"),
    path("reset/<str:token>/", views.reset_password,
         name="reset_password"),
]
