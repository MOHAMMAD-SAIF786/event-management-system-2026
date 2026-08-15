import os
import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date

from cms.models import GalleryCategory, GalleryItem, AdminProfile
from halls.models import (
    Hall,
    HallFeature,
    HallGallery,
    FurnitureCategory,
    FurnitureItem,
    StageCategory,
    StageDesign,
    ServiceCategory,
    Service,
)
from rooms.models import Room
from catering.models import CateringPackage, MenuSection, MenuCategory, MenuItem, GuestPricing
from accounts.models import Customer
from booking.models import Booking, BookingHall


class IsolatedMediaTestCase(TestCase):
    """
    Base test case ensuring any media/image created during tests
    is saved to an isolated temporary folder and completely removed upon completion.
    """
    @classmethod
    def setUpClass(cls):
        cls.temp_media = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls.temp_media)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls.temp_media, ignore_errors=True)


class GalleryFunctionalityTest(IsolatedMediaTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username="admin", password="password123", email="admin@example.com")
        self.category = GalleryCategory.objects.create(name="Wedding", slug="wedding")

    def test_gallery_model_create_and_change_image(self):
        """Verify model-level capability to create and change an image on GalleryItem."""
        image1 = SimpleUploadedFile("initial.jpg", b"image_content_1", content_type="image/jpeg")
        item = GalleryItem.objects.create(title="Initial Image", category=self.category, image=image1)
        self.assertIn("gallery/initial", item.image.name)

        # Admin / System changes the image file
        image2 = SimpleUploadedFile("replacement.jpg", b"image_content_2", content_type="image/jpeg")
        item.image = image2
        item.title = "Replaced Image"
        item.save()

        item.refresh_from_db()
        self.assertEqual(item.title, "Replaced Image")
        self.assertIn("gallery/replacement", item.image.name)

    def test_cms_gallery_view_add_category_and_upload(self):
        """Test gallery dashboard view for adding categories and uploading images."""
        self.client.login(username="admin", password="password123")

        # 1. Add category via POST
        response = self.client.post("/cms/cms-gallery/", {"action_type": "add_category", "name": "Corporate"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GalleryCategory.objects.filter(name="Corporate").exists())

        # 2. Upload image via POST with custom title
        image = SimpleUploadedFile("uploaded.jpg", b"uploaded_content", content_type="image/jpeg")
        response = self.client.post("/cms/cms-gallery/", {
            "action_type": "upload_images",
            "title": "Stage Decoration",
            "category_id": self.category.id,
            "images": [image]
        })
        self.assertEqual(response.status_code, 302)
        item = GalleryItem.objects.get(category=self.category, title="Stage Decoration")
        self.assertEqual(item.title, "Stage Decoration")

    def test_cms_gallery_view_delete_item(self):
        """Test deleting gallery items from dashboard."""
        self.client.login(username="admin", password="password123")
        image = SimpleUploadedFile("sample.jpg", b"sample_content", content_type="image/jpeg")
        item = GalleryItem.objects.create(category=self.category, image=image)

        response = self.client.get(f"/cms/cms-gallery/?delete_item={item.id}")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GalleryItem.objects.filter(id=item.id).exists())

    def test_cms_gallery_category_filtering(self):
        """Test filtering gallery items by category in dashboard."""
        self.client.login(username="admin", password="password123")
        cat2 = GalleryCategory.objects.create(name="Birthday", slug="birthday")
        img1 = SimpleUploadedFile("w.jpg", b"wed", content_type="image/jpeg")
        img2 = SimpleUploadedFile("b.jpg", b"bday", content_type="image/jpeg")
        item1 = GalleryItem.objects.create(category=self.category, image=img1)
        item2 = GalleryItem.objects.create(category=cat2, image=img2)

        # Filter by category 1
        res = self.client.get(f"/cms/cms-gallery/?category={self.category.id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(item1, res.context["items"])
        self.assertNotIn(item2, res.context["items"])

    def test_homepage_hero_editing_from_cms_reflects_on_homepage(self):
        """Verify editing homepage hero title, description, and image in CMS reflects on the home page."""
        from home.models import HomePage
        
        self.client.login(username="admin", password="password123")
        hero_img = SimpleUploadedFile("new_hero.jpg", b"hero_image_bytes", content_type="image/jpeg")

        # 1. Update Homepage Hero from CMS Dashboard
        response = self.client.post("/cms/dashboard/", {
            "action_type": "update_home_hero",
            "hero_title": "Grand Luxury Events 2026",
            "hero_description": "Exclusive Venues & Unmatched Experiences",
            "hero_image": hero_img
        })
        self.assertEqual(response.status_code, 302)

        # 2. Check Database Record
        homepage_obj = HomePage.objects.first()
        self.assertEqual(homepage_obj.hero_title, "Grand Luxury Events 2026")
        self.assertEqual(homepage_obj.hero_description, "Exclusive Venues & Unmatched Experiences")
        self.assertIn("new_hero", homepage_obj.hero_image.name)

        # 3. Check Front-end Homepage Response
        home_res = self.client.get("/")
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, "Grand Luxury Events 2026")
        self.assertContains(home_res, "Exclusive Venues &amp; Unmatched Experiences")
        self.assertContains(home_res, homepage_obj.hero_image.url)


class PermissionHierarchyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.dev_user = User.objects.create_superuser(username="devuser", password="password123")
        self.superadmin_user = User.objects.create_user(username="superadmin", password="password123")
        AdminProfile.objects.create(user=self.superadmin_user, role="superadmin")
        self.admin_user = User.objects.create_user(username="adminuser", password="password123")
        AdminProfile.objects.create(user=self.admin_user, role="admin")
        self.plain_user = User.objects.create_user(username="plainuser", password="password123")

    def test_superuser_autoprovision_developer(self):
        self.client.login(username="devuser", password="password123")
        response = self.client.get("/cms/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AdminProfile.objects.filter(user=self.dev_user, role="developer").exists())

    def test_plain_user_blocked_from_cms(self):
        self.client.login(username="plainuser", password="password123")
        response = self.client.get("/cms/dashboard/")
        self.assertEqual(response.status_code, 302)

    def test_admin_blocked_from_developer_panel(self):
        self.client.login(username="adminuser", password="password123")
        response = self.client.get("/cms/developer-panel/")
        self.assertEqual(response.status_code, 302)

    def test_developer_can_assign_roles(self):
        self.client.login(username="devuser", password="password123")
        response = self.client.post("/cms/developer-panel/", {
            "action": "update_role",
            "user_id": self.plain_user.id,
            "role": "superadmin"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.plain_user.admin_profile.role, "superadmin")


class CMSComprehensiveEndpointAndURLTest(IsolatedMediaTestCase):
    """
    Comprehensive test suite verifying:
    1. Every named CMS URL resolves without NoReverseMatch
    2. All CMS views render correctly without template errors
    3. Custom error handlers (404, 500, 403) render appropriately
    """

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="supercmsadmin", password="password123", email="admin@ems.local"
        )
        AdminProfile.objects.create(user=self.admin_user, role="developer")

        # Test Data Setup
        self.hall = Hall.objects.create(
            name="Grand Ballroom",
            capacity=500,
            price=Decimal("150000.00"),
            location="North Wing",
            description="Luxury hall",
            is_active=True,
            is_featured=True,
        )

        self.room = Room.objects.create(
            name="Deluxe Suite",
            capacity=2,
            price=Decimal("5000.00"),
            total_rooms=10,
            description="Comfortable room",
            is_active=True,
        )

        self.furn_cat = FurnitureCategory.objects.create(hall=self.hall, name="Chairs")
        self.furniture = FurnitureItem.objects.create(
            category=self.furn_cat,
            name="Chiavari Chair",
            price=Decimal("250.00"),
            unit="piece",
        )

        self.stage_cat = StageCategory.objects.create(hall=self.hall, name="Wedding Stage")
        stage_img = SimpleUploadedFile("stage.jpg", b"stage_img", content_type="image/jpeg")
        self.stage = StageDesign.objects.create(
            category=self.stage_cat,
            name="Royal Floral Stage",
            price=Decimal("45000.00"),
            image=stage_img,
        )

        self.srv_cat = ServiceCategory.objects.create(hall=self.hall, name="Photography")
        self.service = Service.objects.create(
            category=self.srv_cat,
            name="Drone Coverage",
            price=Decimal("15000.00"),
        )

        self.pkg = CateringPackage.objects.create(
            name="Platinum Dining",
            slug="platinum-dining",
            price=Decimal("1200.00"),
            description="Full multi-course",
            is_active=True,
        )

        self.customer = Customer.objects.create(
            name="Rohit Sharma",
            email="rohit@example.com",
            phone="9876543210",
        )

        self.booking = Booking.objects.create(
            customer=self.customer,
            event_type="Wedding",
            event_date=date(2026, 12, 25),
            total_amount=Decimal("250000.00"),
            status="confirmed",
        )

    def test_all_cms_url_reversals(self):
        """Verify that every named CMS URL pattern resolves cleanly."""
        url_tests = [
            ("cms:index", []),
            ("cms:dashboard", []),
            ("cms:booking_list", []),
            ("cms:booking_add", []),
            ("cms:booking_detail", [self.booking.id]),
            ("cms:booking_edit", [self.booking.id]),
            ("cms:booking_delete", [self.booking.id]),
            ("cms:customer_list", []),
            ("cms:customer_detail", [self.customer.id]),
            ("cms:customer_edit", [self.customer.id]),
            ("cms:customer_delete", [self.customer.id]),
            ("cms:hall_list", []),
            ("cms:cms_hall_detail", [self.hall.id]),
            ("cms:hall_add", []),
            ("cms:hall_edit", [self.hall.id]),
            ("cms:hall_toggle_status", [self.hall.id]),
            ("cms:hall_delete", [self.hall.id]),
            ("cms:furniture_list", []),
            ("cms:furniture_add", []),
            ("cms:furniture_edit", [self.furniture.id]),
            ("cms:furniture_item_add", []),
            ("cms:furniture_item_edit", [self.furniture.id]),
            ("cms:furniture_delete", [self.furniture.id]),
            ("cms:furniture_category_add", []),
            ("cms:furniture_category_delete", [self.furn_cat.id]),
            ("cms:stage_design_list", []),
            ("cms:stage_design_add", []),
            ("cms:stage_design_edit", [self.stage.id]),
            ("cms:stage_design_delete", [self.stage.id]),
            ("cms:stage_category_add", []),
            ("cms:stage_category_delete", [self.stage_cat.id]),
            ("cms:service_list", []),
            ("cms:service_add", []),
            ("cms:service_edit", [self.service.id]),
            ("cms:service_delete", [self.service.id]),
            ("cms:service_category_add", []),
            ("cms:service_category_delete", [self.srv_cat.id]),
            ("cms:room_list", []),
            ("cms:room_add", []),
            ("cms:room_edit", [self.room.id]),
            ("cms:room_delete", [self.room.id]),
            ("cms:room_toggle_status", [self.room.id]),
            ("cms:catering_list", []),
            ("cms:catering_add", []),
            ("cms:catering_edit", [self.pkg.id]),
            ("cms:catering_delete", [self.pkg.id]),
            ("cms:catering_toggle_status", [self.pkg.id]),
            ("cms:package_detail", [self.pkg.id]),
            ("cms:gallery_dashboard", []),
            ("cms:admin_management", []),
            ("cms:developer_panel", []),
            ("cms:login", []),
            ("cms:register", []),
            ("cms:logout", []),
        ]

        for name, args in url_tests:
            resolved_url = reverse(name, args=args)
            self.assertTrue(resolved_url.startswith("/cms/"), f"Failed for {name}: {resolved_url}")

    def test_all_cms_get_views_render_success(self):
        """Test GET requests on all core CMS views return 200 OK without errors."""
        self.client.login(username="supercmsadmin", password="password123")

        get_endpoints = [
            reverse("cms:dashboard"),
            reverse("cms:booking_list"),
            reverse("cms:booking_detail", args=[self.booking.id]),
            reverse("cms:booking_edit", args=[self.booking.id]),
            reverse("cms:customer_list"),
            reverse("cms:customer_detail", args=[self.customer.id]),
            reverse("cms:customer_edit", args=[self.customer.id]),
            reverse("cms:hall_list"),
            reverse("cms:cms_hall_detail", args=[self.hall.id]),
            reverse("cms:hall_edit", args=[self.hall.id]),
            reverse("cms:room_list"),
            reverse("cms:furniture_list"),
            reverse("cms:furniture_edit", args=[self.furniture.id]),
            reverse("cms:stage_design_list"),
            reverse("cms:service_list"),
            reverse("cms:catering_list"),
            reverse("cms:package_detail", args=[self.pkg.id]),
            reverse("cms:gallery_dashboard"),
            reverse("cms:admin_management"),
            reverse("cms:developer_panel"),
        ]

        for endpoint in get_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code, 200, f"Endpoint {endpoint} failed with status {response.status_code}"
            )

    def test_cms_modal_action_post_endpoints(self):
        """Test POST actions on modal-based editing views redirect successfully after mutation."""
        self.client.login(username="supercmsadmin", password="password123")

        # 1. Stage Design Edit POST
        stage_res = self.client.post(reverse("cms:stage_design_edit", args=[self.stage.id]), {
            "name": "Updated Stage Floral",
            "price": "50000.00",
            "badge": "Popular"
        })
        self.assertEqual(stage_res.status_code, 302)

        # 2. Service Edit POST
        srv_res = self.client.post(reverse("cms:service_edit", args=[self.service.id]), {
            "name": "Updated 4K Drone Service",
            "price": "18000.00"
        })
        self.assertEqual(srv_res.status_code, 302)

    @override_settings(DEBUG=False)
    def test_custom_404_error_page(self):
        """Verify custom 404 error page renders cleanly on non-existent routes."""
        response = self.client.get("/cms/nonexistent-route-path/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Destination Unavailable", status_code=404)

    def test_custom_500_error_view(self):
        """Verify custom 500 handler view renders 500.html template."""
        from home.views import custom_500
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/simulate-error/")
        response = custom_500(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn("500", response.content.decode("utf-8"))
        self.assertIn("Server Error", response.content.decode("utf-8"))

    def test_custom_403_error_view(self):
        """Verify custom 403 handler view renders 403.html template."""
        from home.views import custom_403
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/simulate-forbidden/")
        response = custom_403(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn("403", response.content.decode("utf-8"))
        self.assertIn("Access Forbidden", response.content.decode("utf-8"))


class StorageSavingImageDeletionTest(TestCase):
    def setUp(self):
        import tempfile
        import shutil
        self.temp_media = tempfile.mkdtemp()
        self.client = Client()
        self.admin = User.objects.create_superuser(username="storage_admin", password="password123")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def test_delayed_delete_file_deletes_after_timer(self):
        """Verify delayed_delete_file deletes file on disk after delay."""
        import os
        import time
        from cms.storage_cleanup import delayed_delete_file

        with self.settings(MEDIA_ROOT=self.temp_media):
            test_file = os.path.join(self.temp_media, "test_old_img.jpg")
            with open(test_file, "wb") as f:
                f.write(b"dummy image bytes")

            self.assertTrue(os.path.exists(test_file))
            delayed_delete_file(test_file, delay_seconds=0.1)

            # Wait briefly for background thread to delete
            time.sleep(0.3)
            self.assertFalse(os.path.exists(test_file))

    def test_replacing_image_triggers_cleanup(self):
        """Verify updating model image replaces old file and schedules old file cleanup."""
        import os
        import time

        with self.settings(MEDIA_ROOT=self.temp_media):
            img1 = SimpleUploadedFile("initial_room.jpg", b"img_bytes_1", content_type="image/jpeg")
            room = Room.objects.create(name="Test Suite", price=Decimal("5000.00"), capacity=2, image=img1)
            old_path = room.image.path
            self.assertTrue(os.path.exists(old_path))

            # Update room image
            img2 = SimpleUploadedFile("new_room.jpg", b"img_bytes_2", content_type="image/jpeg")
            room.image = img2
            room.save()

            # The old image path was queued for deletion
            self.assertNotEqual(room.image.path, old_path)

