# Celuvia Images

**Celuvia Images** is a Django-based eCommerce store for buying and selling
framed image products. The idea is that vendors can create stores and
upload images they want to sell. Celuvia Images print and frame the images
and take a percentage of sales.

Buyers can browse images on the home page, search for images containing
specific words or view and filer by categories.
Images are available in different sizes and frame colors.

Vendors can have multiple stores. They can create and manage their own stores,
upload new and manage products through a vendor dashboard.

## 🌟 Features

### User Accounts

- Users can register as buyers (customers) or vendors
- **Group permissions** are automatically assigned at signup
- Separate signup forms for buyers and vendors
- Vendors can own and manage multiple stores
- Vendors can also purchase products

### Buyers

- Buyers can:
  - view products
  - search of filter by category
  - purchase products
  - receive email notification of their orders \*(printed in the terminal)
  - view their order history
  - leave reviews on all products and edit or delete their reviews
  - reviews ae marked as verified if the user has purchased the item

### Vendor Store Management

- Vendors can:
  - create and manage their stores
  - add, edit, close and reopen their stores
  - add, edit, archive and unarchive their products
  - receive email confirmation of orders from their store(s) \*(printed in the terminal)
  - view orders from their stores
  - vendor accounts also have same permissions as buyer accounts

### Shop

- products are available in **small**, **medium** and **large** sizes
- products are available in **black**, **oak**, **white** and **silver** frame colours
- carts use django sessions and expire after **7 days**
- checkout is handle by an external **Stripe** hosted payment page

## Tech Stack

- **Python 3.13.3**
- **Django 5.2.6**
- **JavaScipt**
- **Bootstrap 5**
- **Google Fonts** - Montserrat & Raleway
- **MariaDb** database
- **Stripe Checkout**
- **Font Awesome**

## App Structure

- accounts

  - user authentication
  - user registration
  - user group assignment of buyers and vendors

- shop
  - manages stores
  - manages products
  - manages cart and cart sessions
  - manages store orders
  - manages user reviews

## Data Models

### Accounts App Models

```
class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address_1 = models.CharField(max_length=50, blank=True)
    address_2 = models.CharField(max_length=50, blank=True)
    town = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

class ResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)
```

### Shop App Models

```
class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="stores")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

class Product(models.Model):
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

class Size(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="sizes")
    small_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    medium_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    large_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

class Review(models.Model):
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

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="orders")
    total = models.DecimalField(max_digits=10, decimal_places=2,
                                default=Decimal(0.00))
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.ForeignKey("Address", on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name="shipping_orders")
    billing_address = models.ForeignKey("Address", on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name="billing_orders")

class OrderItem(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
    ]
    FRAME_CHOICES = [
        ("Black", "Black"),
        ("Oak", "Oak"),
        ("Silver", "Silver"),
        ("White", "White"),
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

class Address(models.Model):
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
```

## Setup of Database & Stripe

### MariaDB setup

I have provided a data dump of my MariaDB database for previously created content and files.

- download revelvant version of MariaDB from [mariadb.org](https://mariadb.org/download/?t=mariadb&p=mariadb&r=12.0.2&os=windows&cpu=x86_64&pkg=msi&mirror=xtom_ams)
- follow installation insructions
- open mariadb command prompt
- create the database and user

  ```
  CREATE DATABASE celuvia_images CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
  CREATE USER 'celuvia_admin@localhost' IDENTIFIED BY 'your_password';
  GRANT ALL PRIVILEGES ON celuvia_images.* TO 'celuvia_user'@'localhost';
  FLUSH PRIVILEGES;
  ```

- ensure the environment variables are configured in the project **settings.py** file

  ```
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.mysql",
          "NAME": "celuvia_db",
          "USER": "celuvia_admin",
          "PASSWORD": "hyperionDev",
          "HOST": "localhost",
          "PORT": "3306",
      }
  }
  ```

- import the provided data dump file (celuvia_images.sql)

  ```
  mysql -u celuvia_admin -p celuvia_images < celuvia_images_dump.sql
  ```

### Stripe setup

- create an account at [stripe.com](stripe.com)
- navigate to your test dashboard
- get your test key - **Publishable Key** and **Secret Key**
- create a **.env** file in your project root folder - _same level as where you project manage.py file is located_
- add the keys to the **.env**

  ```
  STRIPE_PUBLIC_KEY=pk_test_...
  STRIPE_SECRET_KEY=sk_test_...
  ```

- to test payments locally:

  - to test events enter this command in the terminal:

    ```
    stripe listen --forward-to localhost:8000/stripe/webhook/
    ```

  - the above command will provide a **STRIPE_WEBHOOK_SECRET** key
  - add the key to the **.env** file below the 2 previous keys
  - stripe test card no.: 4242 4242 4242 4242
  - test expiry date: any **mm/yy** in future
  - test cvc number: and **3digit number**
  - payment events are sent to the webhook where **stripe listen** was ran

### Cart & Checkout

- carts are stored in django sessions and expire 7 days after the cart was created
- session expiry is reset to 7 days when the cart is modified
- when users checkout, they fill in address forms for shipping and billing addresses
- if users enter an address at signup, this is prepopulated at checkout as the default address
- if billing address is the same as the shipping address, the billing for is not needed and hidden
- on successful paymentt, an order details email is sent to the user and store owner

### Reviews

- all signed in users can submit a product review
- reviews are displayed below the product on the product detail page
- on the home page, ratings and review count are visible on product cards

## Design and Frontend

- **Bootstrap** for responsive styling
- **Google Fonts**:
  - _Montserrat_ for headings and titles
  - _Raleway_ for paragraphs, lists, links
- **Font Awesome** for rating stars
- Custom **CSS** for styling of body and to override some bootstrap styling
- Custom **JavaScript** for form view toggling, form prepopulation to enhance user experience

## Future Improvements

There are some future enhancement that could be added that I never considered
due to time contraints.

- Enable other paymennt methods such as Google Pay, Paypal and Apple Pay
- Provide monthly store reports that:
  - provide sales breakdown and profist after Celuvia Images % is taken
  - track sales of products
  - allow vendors to set their price, and Celuvia add the costs on top
- For store owners, provide just 1 email for orders grouped by stores they own,
  as they currently reveive an email per store
- Ensure owners cannot add reviews to their own products
- Expand to allow for international customers and currencies
- Provide a customised internal Stripe checkout page

## Acknowlegments

- **[Django](https://docs.djangoproject.com/en/5.2/)** documentation
- **[bootstrap 5](https://getbootstrap.com/)**
- **[Google Fonts](https://fonts.google.com/)**
- **[Font Awesome](https://fontawesome.com/)**
- **[Stripe](https://docs.stripe.com/development)** Developer Resources
- **[Piaxbay](pixabay.com)** Images
- **[Stack Overflow](stackoverflow.com)**
- **[W3 Schools](w3schools.com)**
