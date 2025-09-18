from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Store, Product
from .forms import StoreForm, ProductForm


@login_required
def vendor_dashboard(request):
    """
    Dashboard for a vendor to manage their store(s).
    """
    if not request.user.is_vendor():
        return HttpResponseForbidden()
    stores = request.user.stores.all()
    return render(request, "shop/vendor_dashboard.html", {"stores": stores})


@login_required
def store_detail(request, store_id):
    """
    Detail page for managing a stores products.
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    query = request.GET.get("q")
    products = store.products.all()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, "shop/store_detail.html",
                  {"store": store, "products": products, "query": query})


@login_required
def create_store(request):
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
            return redirect("shop:store_detail", store_id=store.id)
    else:
        form = StoreForm()
    return render(request, "shop/store_form.html", {"form": form})


@login_required
def edit_store(request, store_id):
    """
    Edit an existing store. Restricted to store owner.
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect("shop:store_detail", store_id=store.id)
    else:
        form = StoreForm(instance=store)
    return render(request, "shop/store_form.html",
                  {"form": form, "edit": True, "store": store})


@login_required
def close_store(request, store_id):
    """
    Allows an owner to close a store
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        store.is_active = False
        store.save()
        return redirect("shop:vendor_dashboard")
    return render(request, "shop/close_store_confirm.html", {"store": store})


@login_required
def add_product(request, store_id):
    """
    Allows owner to add new products.
    """
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
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
    product = get_object_or_404(
        Product, id=product_id, store__owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("shop:store_detail", store_id=product.store.id)
    else:
        form = ProductForm(instance=product)
    return render(
        request,
        "shop/add_product.html",
        {"form": form, "store": product.store,
         "edit": True, "product": product},
    )
