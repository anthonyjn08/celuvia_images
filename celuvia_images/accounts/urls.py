from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    # Signup views
    path("signup/", views.buyer_signup, name="signup_buyer"),
    path("signup/vendor/", views.vendor_signup, name="signup_vendor"),

    # Login/Logout views
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Password reset views
    path("reset/", views.request_password_reset,
         name="request_password_reset"),
    path("reset/<str:token>/", views.reset_password,
         name="reset_password"),
]
