from django.db import models
from django.db.models import Avg
from accounts.models import User


class Store(models.Model):
    """
    Model representing a vendor's store.

    Fields:
        - owner: ForeignKey to the vendor User who owns the store.
        - name: CharField for the store's name (max length 200).
        - description: TextField for a short description of the store.
    """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

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
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing a framed image product.

    FRAME_CHOICES:
        - Available frame color options for the product.

    SIZE_CHOICES:
        - Available size options for the product.

    Fields:
        - store: ForeignKey linking product to the vendor's Store.
        - category: ForeignKey linking product to a Category (nullable).
        - name: CharField for the product's name (max length 200).
        - frame_colour: CharField with choices from FRAME_CHOICES.
        - size: CharField with choices from SIZE_CHOICES.
        - description: TextField for the product description.
        - image: ImageField storing uploaded product images.
        - price: DecimalField for product price (max 10 digits, 2 decimal
          places).
        - stock: PositiveIntegerField tracking product stock level.
        - created_at: DateTimeField set when the product is created.

    Meta:
        - unique_together: Prevents duplicate product variations in same store.
    """
    FRAME_CHOICES = [
        ("black", "Black"),
        ("white", "White"),
        ("silver", "Silver"),
        ("oak", "Oak"),
    ]

    SIZE_CHOICES = [
        ("small", "30x40cm"),
        ("medium", "50x70cm"),
        ("large", "70x100cm"),
    ]

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    frame_colour = models.CharField(max_length=20, choices=FRAME_CHOICES)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "name", "frame_colour", "size")

    def __str__(self):
        return f"{self.name} - {self.frame_colour}/{self.size}"

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


class Review(models.Model):
    """
    Model for buyer reviews of products.

    Fields:
        - product: ForeignKey linking to the reviewed Product.
        - user: ForeignKey linking to the reviewing User.
        - rating: PositiveIntegerField for review rating (default 5).
        - comment: TextField for review content.
        - verified: BooleanField, True if buyer purchased the product.
        - created_at: DateTimeField for review creation date.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} review on {self.product.name}"


class Order(models.Model):
    """
    Model representing a buyer's order.

    Fields:
        - buyer: ForeignKey to the User who placed the order.
        - created_at: DateTimeField for when the order was placed.
        - total: DecimalField for the order total amount.
        - email_sent: BooleanField, True if invoice email has been sent.
    """
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.buyer.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} (x{self.quantity})"
