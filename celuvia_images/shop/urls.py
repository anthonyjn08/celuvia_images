from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # Store browsing
    path("", views.home, name="home"),
    path("categories", views.category, name="category"),
    path("category/<slug:category_slug>/",
         views.home, name="category_detail"),
    path("products/<int:product_id>/",
         views.product_detail, name="product_detail"),

    # Vendor dashboard & stores
    path("vendor/dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("vendor/stores/add/", views.add_store, name="add_store"),
    path("vendor/stores/<int:store_id>/",
         views.store_detail, name="store_detail"),
    path("vendor/stores/<int:store_id>/edit/",
         views.edit_store, name="edit_store"),
    path("vendor/stores/<int:store_id>/close/",
         views.close_store, name="close_store"),
    path("vendor/stores/<int:store_id>/reopen/",
         views.reopen_store, name="reopen_store"),

    # Vendor products
    path("vendor/stores/<int:store_id>/add-product/",
         views.add_product, name="add_product"),
    path("vendor/stores/<int:store_id>/products/<int:product_id>/edit/",
         views.edit_product, name="edit_product"),
    path("vendor/stores/<int:store_id>/products/<int:product_id>/archive/",
         views.archive_product, name="archive_product"),
    path("vendor/stores/<int:store_id>/products/<int:product_id>/unarchive/",
         views.unarchive_product, name="unarchive_product"),

    # Vendor orders
    path("vendor/orders/", views.vendor_orders, name="vendor_orders"),

    # Cart
    path("cart/", views.show_cart, name="show_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),

    # Checkout & Stripe
    path("checkout/", views.checkout, name="checkout"),
    path("create-checkout-session/",
         views.create_checkout_session, name="create_checkout_session"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),

    # Reviews
    path("products/<int:product_id>/review/",
         views.add_review, name="add_review"),
    path("review/<int:review_id>/edit/",
         views.edit_review, name="edit_review"),
    path("review/<int:review_id>/delete/",
         views.delete_review, name="delete_review"),

    # Buyer orders
    path("my-orders/", views.my_orders, name="my_orders"),
]
