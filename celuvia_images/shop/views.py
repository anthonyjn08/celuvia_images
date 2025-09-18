from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Store
from .forms import StoreForm


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
