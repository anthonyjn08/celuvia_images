from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .forms import BuyerSignUpForm, VendorSignUpForm

User = get_user_model()


class UserModelTest(TestCase):
    """
    Unit tests for the custom User model using groups.

    These tests validate that Buyer and Vendor users are created correctly
    and assigned to the appropriate groups at signup.
    """
    def setUp(self):
        """
        Set up test users and create user groups.
        """
        # Create Buyer and Vendor groups
        self.buyer_group = Group.objects.create(name="Buyers")
        self.vendor_group = Group.objects.create(name="Vendors")

        # Create a buyer account and adds them to the buyers group
        self.buyer = User.objects.create_user(
            email="buyer@test.com",
            first_name="Buyer",
            last_name="User",
            password="buyeruser123"
        )
        self.buyer.groups.add(self.buyer_group)

        # Create a vendor account and add them to vendor group
        self.vendor = User.objects.create_user(
            email="vendor@test.com",
            first_name="Vendor",
            last_name="User",
            password="vendoruser123"
        )
        self.vendor.groups.add(self.vendor_group)

    def test_buyer_creation(self):
        """
        Ensure the Buyer user is created correctly and belongs to the
        Buyers group.
        """
        user = User.objects.get(email="buyer@test.com")

        # Verify users details and user group
        self.assertEqual(user.first_name, "Buyer")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("buyeruser123"))
        self.assertTrue(user.is_buyer())
        self.assertFalse(user.is_vendor())

    def test_vendor_creation(self):
        """
        Ensure the Vendor user is created correctly and belongs to the
        Vendors group.
        """
        user = User.objects.get(email="vendor@test.com")

        # Verify users details and user group
        self.assertEqual(user.first_name, "Vendor")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("vendoruser123"))
        self.assertTrue(user.is_vendor())
        self.assertFalse(user.is_buyer())


class UserSignupFormTest(TestCase):
    """
    Tests the functionality of the Buyer and Vendor signup forms.

    The tests validate that form submissions create users and assign them
    to the correct groups.
    """
    def setUp(self):
        """
        Create the user groups.
        """
        # Create Buyer and Vendor groups
        self.buyer_group = Group.objects.create(name="Buyers")
        self.vendor_group = Group.objects.create(name="Vendors")

    def test_buyer_signup_form(self):
        """
        Test to make sure that completing and submitting the BuyerSignupForm
        creates a user.
        """
        form_data = {
            "email": "buyer@test.com",
            "first_name": "New",
            "last_name": "Buyer",
            "password1": "buyeruser123",
            "password2": "buyeruser123",
        }

        form = BuyerSignUpForm(data=form_data)

        # Ensure form is valid
        self.assertTrue(form.is_valid())
        user = form.save()

        # Assign user group
        buyers_group = Group.objects.get(name="Buyers")
        user.groups.add(buyers_group)

        # Verify user details assigned to Buyers group
        self.assertEqual(user.email, "buyer@test.com")
        self.assertTrue(user.check_password("buyeruser123"))
        self.assertTrue(user.is_buyer())

    def test_vendor_signup_form(self):
        """
        Test to make sure that completing and submitting the VendorSignupForm
        creates a user.
        """
        form_data = {
            "email": "vendor@test.com",
            "first_name": "New",
            "last_name": "Vendor",
            "password1": "vendoruser123",
            "password2": "vendoruser123",
        }

        form = VendorSignUpForm(data=form_data)

        # Ensure form is valid
        self.assertTrue(form.is_valid())
        user = form.save()

        # Assign user group
        vendors_group = Group.objects.get(name="Vendors")
        user.groups.add(vendors_group)

        # Verify user details assigned to Vendors group
        self.assertEqual(user.email, "vendor@test.com")
        self.assertTrue(user.check_password("vendoruser123"))
        self.assertTrue(user.is_vendor())


class AccountsViewsTest(TestCase):
    """
    These test the account views for buyer signup, vendor signup
    and user login.

    These tests validate that buyers and vendors can sign up correctly,
    are assigned to the correct groups, and that login works as expected.
    """
    def setUp(self):
        """
        Create Buyer and Vendor groups for testing.
        """
        self.buyer_group = Group.objects.create(name="Buyers")
        self.vendor_group = Group.objects.create(name="Vendors")

    def test_buyer_signup_view(self):
        """
        Ensure a new Buyer user is created and correctly assigned to
        the Buyers group.
        """
        response = self.client.post(reverse("accounts:signup_buyer"), {
            "first_name": "Test",
            "last_name": "Buyer",
            "email": "buyer@test.com",
            "password1": "buyeruser123",
            "password2": "buyeruser123",
        }, follow=True)

        # Verify redirect
        self.assertRedirects(response, reverse("shop:home"))

        # Verify user details assigned to Buyers group
        user = User.objects.get(email="buyer@test.com")
        self.assertTrue(user.is_buyer())
        self.assertFalse(user.is_vendor())

        # Verify user is logged in
        self.assertIn("_auth_user_id", self.client.session)

    def test_vendor_signup_view(self):
        """
        Ensure a new Vendor user is created and correctly assigned to
        the Vendors group.
        """
        response = self.client.post(reverse("accounts:signup_vendor"), {
            "first_name": "Test",
            "last_name": "Vendor",
            "email": "vendor@test.com",
            "password1": "vendoruser123",
            "password2": "vendoruser123",
        }, follow=True)

        # Verify redirect
        self.assertRedirects(response, reverse("shop:vendor_dashboard"))

        # Verify user details assigned to Vendors group
        user = User.objects.get(email="vendor@test.com")
        self.assertTrue(user.is_vendor())
        self.assertFalse(user.is_buyer())

        # Verify user is logged in
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_view(self):
        """
        Ensure an existing user can log in with valid credentials.
        """
        # Create user
        User.objects.create_user(
            email="login@test.com",
            first_name="Login",
            last_name="User",
            password="testpass123"
        )

        # Log in
        response = self.client.post(reverse("accounts:login"), {
            "email": "login@test.com",
            "password": "testpass123",
        }, follow=True)

        # Redirect check
        self.assertRedirects(response, reverse("shop:home"))

        # Verify user is in current session
        self.assertIn("_auth_user_id", self.client.session)
