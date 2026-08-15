from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Customer
from accounts.services import CustomerAuthManager, BaseAuthProvider, LocalDjangoAuthProvider
from accounts.session_auth import (
    CUSTOMER_SESSION_KEY,
    CMS_ADMIN_SESSION_KEY,
    customer_login,
    customer_logout,
    cms_admin_login,
    cms_admin_logout,
)
from cms.models import AdminProfile


class MockThirdPartyOAuthProvider(BaseAuthProvider):
    """
    Mock 3rd-party provider (e.g. Google/Firebase) for testing modular auth.
    """
    def authenticate(self, credentials):
        token = credentials.get("token")
        if token == "valid_google_token":
            email = "oauth_user@gmail.com"
            user, _ = User.objects.get_or_create(username="oauth_user", email=email, first_name="Google User")
            return user
        return None

    def register(self, data):
        user = User.objects.create_user(username="new_oauth_user", email="new_oauth@gmail.com", first_name="New OAuth")
        customer = Customer.objects.create(user=user, name="New OAuth", email="new_oauth@gmail.com")
        return user, customer

    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class ModularAuthServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="localuser",
            email="local@example.com",
            password="SecurePassword123!",
            first_name="Local User",
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name="Local User",
            email="local@example.com",
            phone="9988776655",
        )

    def test_local_provider_auth_by_username(self):
        auth_user = CustomerAuthManager.authenticate("local", username="localuser", password="SecurePassword123!")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.pk, self.user.pk)

    def test_local_provider_auth_by_email(self):
        auth_user = CustomerAuthManager.authenticate("local", username="local@example.com", password="SecurePassword123!")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.pk, self.user.pk)

    def test_local_provider_invalid_password(self):
        auth_user = CustomerAuthManager.authenticate("local", username="localuser", password="WrongPassword!")
        self.assertIsNone(auth_user)

    def test_pluggable_third_party_provider_registration(self):
        CustomerAuthManager.register_provider("mock_google", MockThirdPartyOAuthProvider())
        user = CustomerAuthManager.authenticate("mock_google", token="valid_google_token")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "oauth_user@gmail.com")


class DualSessionSeparationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Customer User
        self.customer_user = User.objects.create_user(
            username="customer_alice",
            email="alice@example.com",
            password="AlicePassword123!",
            first_name="Alice Customer",
        )
        self.customer_profile = Customer.objects.create(
            user=self.customer_user,
            name="Alice Customer",
            email="alice@example.com",
            phone="1122334455",
        )

        # 2. CMS Admin User
        self.admin_user = User.objects.create_user(
            username="admin_bob",
            email="bob@admin.com",
            password="BobPassword123!",
            first_name="Bob Admin",
            is_staff=True,
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            role="admin",
        )

    def test_customer_registration_and_login_flow(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "Charlie Customer",
                "username": "charlie",
                "email": "charlie@example.com",
                "phone": "5566778899",
                "password": "CharliePassword123",
                "confirm_password": "CharliePassword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get(CUSTOMER_SESSION_KEY), str(User.objects.get(username="charlie").id))
        self.assertIsNone(self.client.session.get(CMS_ADMIN_SESSION_KEY))

    def test_dual_session_coexistence(self):
        # 1. Login Customer
        res_cust = self.client.post(
            reverse("accounts:user_login"),
            {"username": "customer_alice", "password": "AlicePassword123!"},
        )
        self.assertEqual(res_cust.status_code, 302)
        self.assertEqual(self.client.session.get(CUSTOMER_SESSION_KEY), str(self.customer_user.id))

        # 2. Login CMS Admin
        res_admin = self.client.post(
            reverse("cms:admin_login"),
            {"username": "admin_bob", "password": "BobPassword123!"},
        )
        self.assertEqual(res_admin.status_code, 302)

        # Both session keys MUST exist simultaneously
        session = self.client.session
        self.assertEqual(session.get(CUSTOMER_SESSION_KEY), str(self.customer_user.id))
        self.assertEqual(session.get(CMS_ADMIN_SESSION_KEY), str(self.admin_user.id))

        # 3. Access customer profile -> should resolve Customer Alice
        profile_res = self.client.get(reverse("accounts:profile"))
        self.assertEqual(profile_res.status_code, 200)
        self.assertContains(profile_res, "Alice Customer")

        # 4. Access CMS dashboard -> should resolve Admin Bob
        cms_res = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(cms_res.status_code, 200)
        self.assertContains(cms_res, "Dashboard")

        # 5. Logout customer only -> Admin session remains active
        logout_cust = self.client.get(reverse("accounts:user_logout"))
        self.assertEqual(logout_cust.status_code, 302)
        session_after_cust_logout = self.client.session
        self.assertIsNone(session_after_cust_logout.get(CUSTOMER_SESSION_KEY))
        self.assertEqual(session_after_cust_logout.get(CMS_ADMIN_SESSION_KEY), str(self.admin_user.id))

        # CMS dashboard still accessible
        cms_res_after = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(cms_res_after.status_code, 200)

        # 6. Logout CMS admin only -> CMS session removed
        logout_admin = self.client.get(reverse("cms:admin_logout"))
        self.assertEqual(logout_admin.status_code, 302)
        session_after_admin_logout = self.client.session
        self.assertIsNone(session_after_admin_logout.get(CMS_ADMIN_SESSION_KEY))

    def test_public_page_login_logout_flow(self):
        """Test full login, navbar rendering, and logout flow on public pages."""
        # 1. Login
        res_login = self.client.post(
            reverse("accounts:user_login"),
            {"username": "customer_alice", "password": "AlicePassword123!"},
        )
        self.assertEqual(res_login.status_code, 302)

        # 2. Check public page shows authenticated user dropdown and Logout button
        home_res = self.client.get("/")
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, "Logout")
        self.assertContains(home_res, "Alice")

        # 3. Trigger public logout
        logout_res = self.client.get(reverse("accounts:user_logout"), follow=True)
        self.assertEqual(logout_res.status_code, 200)

        # 4. Check public page now shows Login/Register buttons and NOT Logout
        self.assertContains(logout_res, "Login")
        self.assertContains(logout_res, "Register")
        self.assertNotContains(logout_res, "My Bookings")

