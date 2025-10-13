from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

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
        self.assertEqual(user.first_name, "Vendor")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("vendoruser123"))
        self.assertTrue(user.is_vendor())
        self.assertFalse(user.is_buyer())
