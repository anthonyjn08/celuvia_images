from django import forms
from .models import Store, Product, Review, Size


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
        - description: CharField, product description
        - image: ImageField, product image
    """
    class Meta:
        model = Product
        fields = ["category", "name", "description", "image"]
        widgets = {
            "category": forms.TextInput(
                attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control"}),
            "description": forms.TextInput(
                attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}),
            }


class SizeForm(forms.ModelForm):
    """
    Form for price by image size.

    Fields:
        - small_price: DecimalField, product price
        - medium_price: DecimalField, product price
        - large_price: DecimalField, product price
    """
    class Meta:
        model = Size
        fields = ["small_price", "medium_price", "large_price"]
        widgets = {
            "small_price": forms.NumberInput(
                attrs={"class": "form-control"}),
            "medium_price": forms.NumberInput(
                attrs={"class": "form-control"}),
            "large_price": forms.NumberInput(
                attrs={"class": "form-control"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                attrs={"class": "form-select"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}),
        }
