from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.db.models import Avg
from django.utils.text import slugify

FRAME_CHOICES = [
        ("Black", "Black"),
        ("Oak", "Oak"),
        ("Silver", "Silver"),
        ("White", "White"),
    ]


class Store(models.Model):
    """
    Model representing a vendor's store.

    Fields:
        - owner: ForeignKey to the vendor User who owns the store.
        - name: CharField for the store's name (max length 200).
        - description: TextField for a short description of the store.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="stores")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @property
    def owner_name(self):
        return self.owner.full_name

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.full_name})"


class Category(models.Model):
    """
    Model representing product categories.

    Fields:
        - name: CharField, unique, for the category name.
        - slug: SlugField, unique, used for URLs and category lookups.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing a framed image product.

    Fields:
        - store: ForeignKey linking product to the vendor's Store.
        - category: ForeignKey linking product to a Category (nullable).
        - name: CharField for the product's name (max length 200).
        - description: TextField for the product description.
        - image: ImageField storing uploaded product images.
        - created_at: DateTimeField set when the product is created.

    Meta:
        - unique_together: Prevents duplicate product variations in same store.
    """
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "name")

    def get_min_price(self):
        if not hasattr(self, "sizes"):
            return None

        prices = [
            self.sizes.small_price,
            self.sizes.medium_price,
            self.sizes.large_price,
        ]
        prices = [p for p in prices if p is not None]
        return min(prices) if prices else None

    def __str__(self):
        return self.name

    def get_average_rating(self):
        """
        Returns the average rating for this product as a decimal.
        If there are no reviews, returns None.
        """
        return self.reviews.aggregate(avg=Avg("rating"))["avg"]

    def get_review_count(self):
        """
        Returns the total number of reviews for this product.
        """
        return self.reviews.count()


class Size(models.Model):
    """
    Model for prcing images by size.

    Fields:
        - Product: OneToOneField, product from the Product list to set
          prices for.
        - small_price: DecimalField, price of small image
        - medium_price: DecimalField, price of medium image
        - large_price: DecimalField, price of large image
    """
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="sizes")
    small_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    medium_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    large_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Sizes for {self.product.name}"


class Review(models.Model):
    """
    Model for buyer reviews of products.

    RATINGE_CHOICES:
        - Available star ratings for the product.

    Fields:
        - product: ForeignKey linking to the reviewed Product.
        - user: ForeignKey linking to the reviewing User.
        - rating: IntegerField for review rating (default 5).
        - comment: TextField for review content.
        - verified: BooleanField, True if buyer purchased the product.
        - created_at: DateTimeField for review creation date.
    """
    RATING_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reviews")
    rating = models.IntegerField(default=5, choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} - {self.product.name} ({self.rating}/5)"


class Order(models.Model):
    """
    Model representing a buyer's order.

    STATUS_CHOICES:
        - Status of order

    Fields:
        - user: ForeignKey to the User who placed the order.
        - created_at: DateTimeField for when the order was placed.
        - status: CharField for the order shipping status.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending")
    shipping_address = models.ForeignKey("Address", on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name="shipping_orders")
    billing_address = models.ForeignKey("Address", on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name="billing_orders")

    def __str__(self):
        return f"Order {self.id} by {self.user.full_name}"


class OrderItem(models.Model):
    """
    Individual items in an order.

    SIZE_CHOICES:
        - Available size options for the product.

    FRAME_CHOICES:
        - Available frame color options for the product.

    Fields:
        - order: ForeignKey, the order from Mrder model.
        - product: ForeignKey, the product from the Product model.
        - quantity: PositiveIntegerField, quantity ordered.
        - frame_colour: CharField, frame colour.
        - size: CharField, frame size.
        - price: DecimalField, item price
    """
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
    ]
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    frame_colour = models.CharField(
        max_length=20, choices=FRAME_CHOICES)
    size = models.CharField(
        max_length=2, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} "
            f"({self.size}/{self.frame_colour})"
            )


class Address(models.Model):
    """
    Stores a users delivery and billing addresses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="addresses")
    full_name = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250, blank=True)
    town = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.address_line1}, {self.city}"
