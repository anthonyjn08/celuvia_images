from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Store, Product, Category, Order, OrderItem, Review
from .forms import StoreForm, ProductForm, ReviewForm


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
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(
                request, f"Product '{product.name}' added to {store.name}.")
            return redirect("shop:store_detail", store_id=store.id)
    else:
        form = ProductForm()
    return render(request, "shop/add_product.html",
                  {"form": form, "store": store})


@login_required
def edit_product(request, product_id):
    """
    Allows owner to edit existing products.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    product = get_object_or_404(
        Product, id=product_id, store__owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect("shop:store_detail", store_id=product.store.id)
    else:
        form = ProductForm(instance=product)
    return render(
        request, "shop/edit_product.html", {"form": form, "product": product})


@login_required
def delete_product(request, product_id):
    """
    Allows owner to delete stores products.
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()

    product = get_object_or_404(
        Product, id=product_id, store__owner=request.user)

    if request.method == "POST":
        store_id = product.store.id
        product.delete()
        messages.warning(request, f"Product '{product.name}' deleted.")
        return redirect("shop:store_detail", store_id=store_id)
    return render(request, "shop/delete_product.html", {"product": product})


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
        # get chosen options from the form
        frame = request.POST.get("frame_colour")
        size = request.POST.get("size")
        quantity = int(request.POST.get("quantity", 1))

        # get or create cart in session
        cart = request.session.get("cart", {})

        # use a unique key for the product + frame + size
        key = f"{product.id}-{frame}-{size}"

        if key in cart:
            cart[key]["quantity"] += quantity
        else:
            cart[key] = {
                "product_id": product.id,
                "frame": frame,
                "size": size,
                "quantity": quantity,
            }

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request, f"{quantity} x {product.name} added to cart.")
        return redirect("shop:product_detail", product_id=product.id)

    return render(request, "shop/product_detail.html", {"product": product})


def show_cart(request):
    """
    View for showing the current user's cart.
    """
    cart = request.session.get("cart", {})
    items, total = [], Decimal("0.00")

    for entry in cart.values():
        product = get_object_or_404(Product, id=entry["product_id"])
        subtotal = product.price * entry["quantity"]
        total += subtotal
        items.append(
            {"product": product, "frame": entry["frame"],
             "size": entry["size"], "quantity": entry["quantity"],
             "subtotal": subtotal}
        )

    return render(request, "shop/cart.html", {"items": items, "total": total})


def update_cart(request):
    """
    Allows users to update or remove items in cart.
    """
    if request.method == "POST":
        key = request.POST.get("key")
        qty = int(request.POST.get("quantity", 0))
        cart = request.session.get("cart", {})
        if key in cart:
            if qty > 0:
                cart[key]["quantity"] = qty
                messages.success(request, "Cart updated.")
            else:
                del cart[key]
                messages.info(request, "Item removed from cart.")
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("shop:show_cart")


@login_required
def checkout(request):
    """
    Checkout for users toc omplete their order order and send
    confirmation email.
    """
    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:product_list")

    if request.method == "POST":
        # create the order
        order = Order.objects.create(user=request.user, total=0)
        total = Decimal("0.00")

        # add items to the order
        for entry in cart.values():
            product = get_object_or_404(Product, id=entry["product_id"])
            qty = entry["quantity"]
            subtotal = product.price * qty
            total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=subtotal,
                frame_colour=entry["frame"],
                size=entry["size"],
            )

        # update order total
        order.total = total
        order.save()

        # send confirmation email
        subject = f"Celuvia Images - Order Confirmation #{order.id}"
        html_body = render_to_string(
            "emails/order_confirmation_email.html", {"order": order})

        email = EmailMessage(subject, html_body, None, [order.user.email])
        email.content_subtype = "html"
        email.send(fail_silently=True)

        # clear the cart
        request.session["cart"] = {}
        request.session.modified = True

        messages.success(request, f"Order #{order.id} placed successfully.")
        return redirect("shop:my_orders")

    return render(request, "shop/checkout.html")


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
