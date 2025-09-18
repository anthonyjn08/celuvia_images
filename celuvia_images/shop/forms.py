from django import forms
from .models import Store, Product


class StoreForm(forms.ModelForm):
    """
    Form for creating or updating a store.

    Fields:
        - name: CharField, store name
        - description: CharField, store description
        - email: EmailField, store email
        - phone_number: CharField, store phone number
    """
    class Meta:
        model = Store
        fields = ["name", "description", "email", "phone_number"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}),
            "description": forms.TextInput(
                attrs={"class": "form-control"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}),
            }


class ProductForm(forms.ModelForm):
    """
    Form for creating or updating a product.

    Fields:
        - category: CharField, product category
        - name: CharField, product name
        - frame_colour: CharField, product frame colour
        - size: CharField, product frame size
        - description: CharField, product description
        - image: ImageField, product image
        - price: DecimalField, product price
        - stock: PositiveIntegerField, product stock quantity
    """
    class Meta:
        model = Product
        fields = ["category", "name", "frame_colour",
                  "size", "description",
                  "image", "price", "stock"]
        widgets = {
            "category": forms.TextInput(
                attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control"}),
            "frame_colour": forms.TextInput(
                attrs={"class": "form-control"}),
            "size": forms.TextInput(
                attrs={"class": "form-control"}),
            "description": forms.TextInput(
                attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01",
                       "min": "0.01"}),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "step": "1", "min": "0"}),
            }
