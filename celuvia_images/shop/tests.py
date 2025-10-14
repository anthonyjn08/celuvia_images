from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Store

User = get_user_model()


class VendorViewsTest(TestCase):
    """
    These tests test that users must be in the vendor group to access the
    vendor dashboard, access store detail, add a store and add a product.
    """

    def setUp(self):
        """
        Create a vendor user, a buyer user, the Vendors group, and log in.
        """
        self.vendor_group = Group.objects.create(name="Vendors")

        # Create vendor user
        self.vendor = User.objects.create_user(
            email="vendor@test.com",
            first_name="Vendor",
            last_name="User",
            password="vendorpass123"
        )
        self.vendor.groups.add(self.vendor_group)

        # Create buyer user
        self.buyer = User.objects.create_user(
            email="buyer@test.com",
            first_name="Buyer",
            last_name="User",
            password="buyerpass123"
        )

        # Create a test store for the vendor
        self.store = Store.objects.create(
            owner=self.vendor,
            name="Test Store",
            description="Test description",
            email="store@test.com",
            phone_number="07777777777"
        )

    # --- Vendor Dashboard Tests ---
    def test_vendor_dashboard(self):
        """
        Check that a user in the vendor group can access dashboard and
        view their stores.
        """

        # Login required to access dashboard
        self.client.login(email="vendor@test.com", password="vendorpass123")

        # Verify dashboard access and status codes
        response = self.client.get(reverse("shop:vendor_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/vendor_dashboard.html")
        self.assertIn(self.store, response.context["stores"])

    def test_vendor_dashboard_forbidden_buyers(self):
        """
        Check that a user with a buyer account can not gain access to
        the vendor dashoard area of the site.
        """

        # Log in the user
        self.client.login(email="buyer@test.com", password="buyerpass123")

        # Ensure the view returns Access Forbidden code
        response = self.client.get(reverse("shop:vendor_dashboard"))
        self.assertEqual(response.status_code, 403)

    # --- Vendor Store Detail tests ---
    def test_store_detail_owner_access(self):
        """
        Check that only a user who is in the Vendors group and is the stores
        owner can view details of their own store(s).
        """

        # Log user in
        self.client.login(email="vendor@test.com", password="vendorpass123")

        # Verify the response, status code and store detail
        response = self.client.get(reverse(
            "shop:store_detail", args=[self.store.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/store_detail.html")
        self.assertEqual(response.context["store"], self.store)

    def test_store_detail_forbidden_for_non_vendor(self):
        """
        Check that buyers cannot access the store detail view.
        """

        # Log buyer user in
        self.client.login(email="buyer@test.com", password="buyerpass123")

        # Verify that access is 403 Forbidden
        response = self.client.get(reverse(
            "shop:store_detail", args=[self.store.id]))
        self.assertEqual(response.status_code, 403)

    def test_store_detail_vendor_non_owner(self):
        """
        Test that a vendor cannot access store they don't own.
        """

        # Create second vendor and assign to Vendors group
        other_vendor = User.objects.create_user(
            email="othervendor@test.com",
            first_name="Other",
            last_name="Vendor",
            password="othervendor123"
        )
        other_vendor.groups.add(self.vendor_group)

        # Log in as the second vendor
        self.client.login(
            email="othervendor@test.com", password="othervendor123")

        # Try to access the store details of another vendors store.
        response = self.client.get(reverse(
            "shop:store_detail", args=[self.store.id]))

        # Verify that the response has a 404 status code
        self.assertEqual(response.status_code, 404)

    # --- Store creation test---
    def test_add_store_view(self):
        """
        Test the add store view creates a new store.
        """

        # Log in user
        self.client.login(email="vendor@test.com", password="vendorpass123")

        # Form data
        form_data = {
            "name": "New Store",
            "description": "Test new store",
            "email": "newstore@test.com",
            "phone_number": "07777777778"
        }

        # Verify response and store creation
        response = self.client.post(reverse(
            "shop:add_store"), form_data, follow=True)
        self.assertRedirects(response, reverse("shop:vendor_dashboard"))
        store = Store.objects.get(name="New Store")
        self.assertEqual(store.owner, self.vendor)

    def test_add_store_forbidden_for_non_vendor(self):
        """
        Test that buyers cannot create a new store.
        """

        # Log in user
        self.client.login(email="buyer@test.com", password="buyerpass123")

        # Verify 403 Forbidden access response
        response = self.client.get(reverse("shop:add_store"))
        self.assertEqual(response.status_code, 403)
