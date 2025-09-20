from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # Store browsing
    path("", views.home, name="home"),
    path("category/<slug:category_slug>/",
         views.category_detail, name="category_detail"),
    path("products/", views.product_list, name="product_list"),
    path("products/category/<slug:category_slug>/",
         views.product_list, name="product_list_by_category"),
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

    # Vendor products
    path("vendor/stores/<int:store_id>/add-product/",
         views.add_product, name="add_product"),
    path("vendor/products/<int:product_id>/edit/",
         views.edit_product, name="edit_product"),
    path("vendor/products/<int:product_id>/delete/",
         views.delete_product, name="delete_product"),

    # Vendor orders
    path("vendor/orders/", views.vendor_orders, name="vendor_orders"),
    path("vendor/orders/update/<int:order_id>/",
         views.update_order_status, name="update_order_status"),

    # Cart & checkout
    path("cart/", views.show_cart, name="show_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("checkout/", views.checkout, name="checkout"),

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
