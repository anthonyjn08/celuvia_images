import stripe
import json
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import (Store, Product, Category, Order, OrderItem, Review,
                     FRAME_CHOICES)
from .forms import StoreForm, ProductForm, ReviewForm, SizeForm

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    """Store landing page."""
    categories = Category.objects.all()
    return render(request, "shop/home.html", {"categories": categories})


@login_required
def vendor_dashboard(request):
    """
    Dashboard for a vendor to manage their store(s).
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    stores = Store.objects.filter(owner=request.user)
    return render(request, "shop/vendor_dashboard.html",
                  {"stores": stores})


@login_required
def store_detail(request, store_id):
    """
    Detail page for managing a stores products.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    products = Product.objects.filter(store=store)

    search = request.GET.get("search")
    if search:
        products = products.filter(name__icontains=search)

    return render(request, "shop/store_detail.html",
                  {"store": store, "products": products})


@login_required
def add_store(request):
    """
    View to create a new store. Restricted to vendors only.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    if request.method == "POST":
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(
                request, f"Store '{store.name}' created successfully.")

            return redirect("shop:vendor_dashboard")
    else:
        form = StoreForm()
    return render(request, "shop/add_store.html", {"form": form})


@login_required
def edit_store(request, store_id):
    """
    Edit an existing store. Restricted to store owner.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, f"Store '{store.name}' updated.")
            return redirect("shop:vendor_dashboard")
    else:
        form = StoreForm(instance=store)
    return render(request, "shop/edit_store.html",
                  {"form": form, "store": store})


@login_required
def close_store(request, store_id):
    """
    Allows an owner to close a store
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        store.is_active = False
        store.save()
        messages.info(request, f"Store '{store.name}' has been closed.")
        return redirect("shop:vendor_dashboard")
    return render(request, "shop/close_store.html", {"store": store})


@login_required
def vendor_orders(request):
    """
    Allows vendors view to orders from their stores.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store_id = request.GET.get("store_id")
    selected_store = int(store_id) if store_id else None
    stores = request.user.stores.all()
    items_qs = OrderItem.objects.filter(
        product__store__owner=request.user
    ).select_related("order", "product", "order__user")

    if selected_store:
        items_qs = items_qs.filter(product__store_id=selected_store)

    orders = {}
    for item in items_qs:
        orders.setdefault(item.order, []).append(item)

    return render(
        request,
        "shop/vendor_orders.html",
        {
            "orders": orders,
            "stores": stores,
            "selected_store": selected_store,
        },
    )


@login_required
@require_POST
def update_order_status(request, order_id):
    """
    Allows vendors to update the status of orders from their stores.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()
    order = get_object_or_404(Order, id=order_id)
    has_items = OrderItem.objects.filter(
        order=order, product__store__owner=request.user).exists()
    if not has_items:
        return HttpResponseForbidden()

    new_status = request.POST.get("status")
    if new_status not in dict(Order.STATUS_CHOICES):
        messages.error(request, "Invalid status.")
    else:
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated.")
    return redirect("shop:vendor_orders")


def category_detail(request, category_slug):
    """
    Allows users to view products by category.
    """
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, store__is_active=True)

    search = request.GET.get("search")
    if search:
        products = products.filter(name__icontains=search)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "shop/category_detail.html",
        {"category": category, "products": page_obj},
    )


@login_required
def add_product(request, store_id):
    """
    Allows owner to add new products.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        size_form = SizeForm(request.POST)

        if product_form.is_valid() and size_form.is_valid():
            product = product_form.save(commit=False)

            # check if a new category was entered
            new_cat = product_form.cleaned_data.get("new_category")
            if new_cat:
                category, created = Category.objects.get_or_create(
                    name=new_cat)
                product.category = category

            product.store = store
            product.save()

            # save size info
            size = size_form.save(commit=False)
            size.product = product
            size.save()

            messages.success(request,
                             f"Product '{product.name}' added successfully.")
            return redirect("shop:store_detail", store_id=store.id)
    else:
        product_form = ProductForm()
        size_form = SizeForm()

    return render(
        request,
        "shop/add_product.html",
        {"product_form": product_form, "size_form": size_form, "store": store},
    )


@login_required
def edit_product(request, store_id, product_id):
    """
    Allows owner to edit existing products.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    size = getattr(product, "size", None)  # assumes related size object exists

    if request.method == "POST":
        product_form = ProductForm(
            request.POST, request.FILES, instance=product)
        size_form = SizeForm(request.POST, instance=size)

        if product_form.is_valid() and size_form.is_valid():
            product = product_form.save(commit=False)

            # handle new category if entered
            new_cat = product_form.cleaned_data.get("new_category")
            if new_cat:
                category, _ = Category.objects.get_or_create(name=new_cat)
                product.category = category

            product.store = store
            product.save()

            size = size_form.save(commit=False)
            size.product = product
            size.save()

            messages.success(
                request, f"Product '{product.name}' updated successfully.")
            return redirect("shop:store_detail", store_id=store.id)
    else:
        product_form = ProductForm(instance=product)
        size_form = SizeForm(instance=size)

    return render(
        request,
        "shop/edit_product.html",
        {
            "store": store,
            "product": product,
            "product_form": product_form,
            "size_form": size_form,
        },
    )


# @login_required
# def delete_product(request, product_id):
#     """
#     Allows owner to delete stores products.
#     """
#     if not request.user.is_vendor():
#         return HttpResponseForbidden()

#     product = get_object_or_404(
#         Product, id=product_id, store__owner=request.user)

#     if request.method == "POST":
#         store_id = product.store.id
#         product.delete()
#         messages.warning(request, f"Product '{product.name}' deleted.")
#         return redirect("shop:store_detail", store_id=store_id)
#     return render(request, "shop/delete_product.html", {"product": product})


@login_required
def archive_product(request, store_id, product_id):
    """
    Archive a product so it's no longer available to buy
    but is kept for order history.
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)

    if request.method == "POST":
        product.is_active = False
        product.save()
        messages.success(request,
                         f"Product '{product.name}' archived successfully.")
        return redirect("shop:store_detail", store_id=store.id)

    return render(
        request,
        "shop/archive_product.html",
        {"store": store, "product": product},
    )


@login_required
def unarchive_product(request, store_id, product_id):
    """
    Unarchive a product so it becomes available to buy again.
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)

    if request.method == "POST":
        product.is_active = True
        product.save()
        messages.success(request, (f"Product '{product.name}' has been "
                                   f"unarchived and is now available "
                                   f"for purchase."))

        return redirect("shop:store_detail", store_id=store.id)

    return render(
        request,
        "shop/unarchive_product.html",
        {"store": store, "product": product},
    )


def product_list(request, category_slug=None):
    """
    Product list view.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(store__is_active=True)

    search = request.GET.get("search")
    if search:
        products = products.filter(name__icontains=search)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "shop/product_list.html",
        {"category": category, "categories": categories, "page_obj": page_obj},
    )


def product_detail(request, product_id):
    """
    Product detail view. Users can add items to cart.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        frame = request.POST.get("frame_colour")
        size = request.POST.get("size")
        quantity = int(request.POST.get("quantity", 1))

        # price lookup by size
        size_obj = product.sizes
        if size == "S":
            price = size_obj.small_price
        elif size == "M":
            price = size_obj.medium_price
        elif size == "L":
            price = size_obj.large_price
        else:
            messages.error(request, "Invalid size selected.")
            return redirect("shop:product_detail", product_id=product.id)

        cart = request.session.get("cart", {})

        if not isinstance(cart, dict):
            cart = {}

        key = f"{product.id}-{size}-{frame}"

        if key in cart:
            cart[key]["quantity"] += quantity
        else:
            cart[key] = {
                "product_id": product.id,
                "frame_colour": frame,
                "size": size,
                "quantity": quantity,
                "price": str(price),
            }

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request,
            f"{quantity} x {product.name} ({size}, {frame}) added to cart."
        )
        return redirect("shop:product_detail", product_id=product.id)

    return render(request, "shop/product_detail.html", {
        "product": product,
        "FRAME_CHOICES": FRAME_CHOICES,
    })


# utils function to generate cart key
def get_cart_key(product_id, size, frame_colour):
    """Generate a unique key for each cart item."""
    return f"{product_id}-{size}-{frame_colour}"


def add_to_cart(request, product_id):
    """
    View to add items to cart.
    """
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get("size")
    frame_colour = request.POST.get("frame_colour")
    
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    # Look up price from Size model
    price_map = {"S": product.sizes.small_price,
                 "M": product.sizes.medium_price,
                 "L": product.sizes.large_price}
    price = price_map.get(size)

    if price is None:
        messages.error(request, "Invalid size selected.")
        return redirect("shop:product_detail", product_id=product.id)

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}

    # Generate unique cart key
    key = get_cart_key(product.id, size, frame_colour)

    # Update quantity if item already in cart
    if key in cart:
        cart[key]["quantity"] += quantity
    else:
        cart[key] = {
            "product_id": product.id,
            "size": size,
            "frame_colour": frame_colour,
            "quantity": quantity,
            "price": str(price),  # JSON serializable
        }

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, f"Added {product.name} ({size}/{frame_colour}) to cart.")
    return redirect("shop:show_cart")


def show_cart(request):
    """
    View for showing the current user's cart.
    """
    cart = request.session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    items, total = [], Decimal("0.00")

    for key, entry in cart.items():
        product = get_object_or_404(Product, id=entry["product_id"])
        price = Decimal(entry["price"])
        subtotal = price * entry["quantity"]
        total += subtotal

        # Generate cart_key for template
        cart_key = f"{product.id}-{entry['size']}-{entry['frame_colour']}"

        items.append({
            "product": product,
            "size": entry["size"],
            "frame_colour": entry["frame_colour"],
            "quantity": entry["quantity"],
            "subtotal": subtotal,
            "price": price,
            "cart_key": cart_key,  # add this
        })

    return render(request, "shop/cart.html", {"items": items, "total": total})


def update_cart(request):
    """
    Allows users to update or remove items in cart.
    """
    if request.method == "POST":
        cart = request.session.get("cart", {})
        if not isinstance(cart, dict):
            cart = {}

        key = request.POST.get("key", "").strip()
        try:
            qty = int(request.POST.get("quantity", 0))
        except ValueError:
            qty = 0

        if key in cart:
            if qty > 0:
                cart[key]["quantity"] = qty
                messages.success(request, f"Cart updated: {key} -> {qty}")
            else:
                del cart[key]
                messages.info(request, f"Item removed from cart: {key}")

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("shop:show_cart")


@login_required
def create_checkout_session(request):
    """
    Creates a Stripe Checkout session with the current cart.
    """
    cart = request.session.get("cart", {}) or {}
    if not isinstance(cart, dict) or not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:show_cart")

    line_items = []
    for entry in cart.values():
        product = Product.objects.get(id=entry["product_id"])
        price = int(Decimal(entry["price"]) * 100)

        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": f"{product.name} ({entry['size']}, {entry['frame_colour']})",
                },
                "unit_amount": price,
            },
            "quantity": entry["quantity"],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri(reverse("shop:checkout_success")),
            cancel_url=request.build_absolute_uri(reverse("shop:checkout_cancel")),
            customer_email=request.user.email,
            metadata={"user_id": request.user.id},
        )
    except stripe.error.AuthenticationError as e:
        print("❌ Stripe authentication error:", e)
        messages.error(request, "Payment configuration error. Please contact support.")
        return redirect("shop:show_cart")

    return redirect(checkout_session.url, code=303)


# def handle_checkout_session(session):
#     """
#     Create an Order + OrderItems in the DB once payment completes.
#     """
#     from .models import Order, OrderItem, Product

#     customer_email = session.get("customer_email")
#     line_items = stripe.checkout.Session.list_line_items(session["id"])

#     try:
#         user = User.objects.get(email=customer_email)
#     except User.DoesNotExist:
#         user = None

#     order = Order.objects.create(
#         user=user,
#         total=0,
#     )

#     order_total = Decimal("0.00")

#     for item in line_items.data:
#         name = item["description"]
#         quantity = item["quantity"]
#         unit_amount = Decimal(item["price"]["unit_amount"]) / 100

#         try:
#             product = Product.objects.get(name__iexact=name.split("(")[0].strip())
#         except Product.DoesNotExist:
#             product = None

#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             size="N/A",
#             frame_colour="N/A",
#             quantity=quantity,
#             price=unit_amount,
#         )

#         order_total += unit_amount * quantity

#     order.total = order_total
#     order.save()

#     print(f"Order {order.id} created for {customer_email}")



@login_required
def checkout(request):
    """
    Alternate checkout entrypoint (creates a session).
    """
    print(settings.STRIPE_WEBHOOK_SECRET)
    cart = request.session.get("cart", {}) or {}
    if not isinstance(cart, dict) or not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:show_cart")

    line_items = []
    for entry in cart.values():
        product = Product.objects.get(id=entry["product_id"])
        price = int(Decimal(entry["price"]) * 100)
        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": f"{product.name} ({entry['size']}, {entry['frame_colour']})"
                },
                "unit_amount": price,
            },
            "quantity": entry["quantity"],
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            customer_email=request.user.email,
            success_url=request.build_absolute_uri("/checkout/success/"),
            cancel_url=request.build_absolute_uri("/checkout/cancel/"),
            metadata={"user_id": request.user.id},
        )
    except stripe.error.AuthenticationError as e:
        print("❌ Stripe authentication error:", e)
        messages.error(request, "Payment configuration error. Please contact support.")
        return redirect("shop:show_cart")

    return redirect(session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    """
    Handles Stripe webhook events securely.
    """
    print(settings.STRIPE_WEBHOOK_SECRET)
    print("webhook hit")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = json.loads(payload)
    except ValueError:
        return HttpResponse(status=400)  # Invalid payload
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)  # Invalid signature

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")

        # Create order
        order = Order.objects.create(user_id=user_id, total=Decimal("0.00"))
        print(f"✅ Payment completed for session {session['id']} (user {user_id})")

        # Clear cart after successful payment
        request.session["cart"] = {}

        # Send confirmation email
        subject = f"Celuvia Images - Order Confirmation #{order.id}"
        html_body = render_to_string("shop/order_confirmation_email.txt", {"order": order})
        email = EmailMessage(subject, html_body, None, [session["customer_email"]])
        email.content_subtype = "html"
        email.send(fail_silently=True)

    return HttpResponse(status=200)


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     print("payload (first 100 chars):", payload[:100])

#     try:
#         event = json.loads(payload)
#     except ValueError:
#         return HttpResponse(status=400)

#     print("event:", event)
#     return HttpResponse(status=200)


@login_required
def checkout_success(request):
    """
    View shown after successful payment.
    """
    return render(request, "shop/checkout_success.html")


@login_required
def checkout_cancel(request):
    """
    View if user cancels payment.
    """
    return render(request, "shop/checkout_cancel.html")


@login_required
def add_review(request, product_id):
    """
    Allows users to review products.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            # mark as verified if user bought this product
            review.verified = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()
            review.save()
            return redirect("shop:product_detail", product_id=product.id)
    else:
        form = ReviewForm()
    return render(
        request, "shop/add_review.html", {"form": form, "product": product})


@login_required
def edit_review(request, review_id):
    """
    Allows users to edit their review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated.")
            return redirect(
                "shop:product_detail", product_id=review.product.id)

    else:
        form = ReviewForm(instance=review)
    return render(request, "shop/edit_review.html",
                  {"form": form, "review": review})


@login_required
def delete_review(request, review_id):
    """
    Allows users to delete their review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == "POST":
        product_id = review.product.id
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("shop:product_detail", product_id=product_id)
    return render(request, "shop/delete_review.html", {"review": review})


@login_required
def my_orders(request):
    """
    Allows users to see their order history.
    """
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "shop/my_orders.html", {"orders": orders})
