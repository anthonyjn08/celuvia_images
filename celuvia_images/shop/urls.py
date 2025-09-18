from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
     # Vendor URLs
     path("vendor/dashboard/",
          views.vendor_dashboard, name="vendor_dashboard"),
     path("store/create/", views.create_store, name="create_store"),
     path("store/<int:store_id>/", views.store_detail, name="store_detail"),
     path("store/<int:store_id>/edit/", views.edit_store, name="edit_store"),
     path("store/<int:store_id>/close/",
          views.close_store, name="close_store"),
     path("store/<int:store_id>/add_product/",
          views.add_product, name="add_product"),
     path("product/<int:product_id>/edit/",
          views.edit_product, name="edit_product"),
     path("product/<int:product_id>/delete/",
          views.delete_product, name="delete_product"),

     # Shop URLs
     path("products/", views.product_list, name="product_list"),
     path("products/category/<slug:category_slug>/",
          views.product_list, name="product_list_by_category"),
     path("product/<int:product_id>/",
          views.product_detail, name="product_detail"),
     path("products/<int:product_id>/review/",
          views.add_review, name="add_review"),
     path("my-orders/", views.my_orders, name="my_orders"),

     # Cart URLs
     path("cart/", views.cart_view, name="cart"),
     path("cart/update/<str:cart_key>/",
          views.update_cart, name="update_cart"),
     path("cart/remove/<str:cart_key>/",
          views.remove_from_cart, name="remove_from_cart"),
     path("checkout/", views.checkout, name="checkout"),
]
