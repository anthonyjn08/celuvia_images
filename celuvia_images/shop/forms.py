from django import forms
from .models import Store, Product, Review, Size, Category, Address


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
    new_category = forms.CharField(
        required=False,
        label="New Category",
        # help_text="If the category you need doesn't exist, enter it here.",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Product
        fields = ["name", "description", "image", "category"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}),
            "description": forms.TextInput(
                attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}),
            "category": forms.Select(
                attrs={"class": "form-select"}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load categories into the dropdown when vendorsd add new product
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Choose an existing category"


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
    """
    Form for adding product reviews.

    Fields:
        - rating: IntegerField, user rating of the product
        - comment: TextField, for user review comments
    """
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                attrs={"class": "form-select"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}),
        }


class CheckoutAddressForm(forms.ModelForm):
    """
    Form for capturing user shipping or billing address during checkout.

    Fields:
        - full_name: CharField, users full name.
        - address_line1: CharField, 1st line of address.
        - address_line2: CharField, 2nd line of address.
        - town: CharField, town address is located in.
        - city: CharField, city address is located in.
        - postcode: CharField, post code for address.
        - phone: CharField, contact number.
    """
    class Meta:
        model = Address
        fields = ["full_name", "address_line1", "address_line2", "town",
                  "city", "postcode", "phone",
                  ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Full Name"}
            ),
            "address_line1": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Address Line 1"}
            ),
            "address_line2": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Address Line 2"}
            ),
            "town": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Town"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City"}
            ),
            "postcode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Postcode"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Allows form prefixes (shipping/billing) and optional fields.
        """
        super().__init__(*args, **kwargs)
        # Required fields
        required_fields = ["full_name", "address_line1", "city",
                           "postcode", "phone"]
        for field_name, field in self.fields.items():
            field.required = field_name in required_fields
            field.widget.attrs.update({"placeholder": field.label})
