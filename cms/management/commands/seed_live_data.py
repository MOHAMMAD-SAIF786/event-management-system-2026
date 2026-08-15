import os
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from home.models import HomePage
from cms.models import AdminProfile, GalleryCategory, GalleryItem
from accounts.models import Customer
from halls.models import (
    Hall,
    HallFeature,
    HallGallery,
    HallPage,
    FurnitureCategory,
    FurnitureItem,
    StageCategory,
    StageDesign,
    ServiceCategory,
    Service,
)
from rooms.models import Room, RoomFeature, RoomPage
from catering.models import CateringPackage, CateringPage, MenuSection, MenuCategory, MenuItem
from booking.models import (
    Booking,
    BookingHall,
    BookingRoom,
    BookingFurniture,
    BookingStage,
    BookingService,
    BookingCatering,
    BookingMenuItem,
)


class Command(BaseCommand):
    help = "Cleans and seeds meaningful data using images from media/image_archive for Halls, Rooms, Catalog, Gallery, and Bookings."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("== Starting Comprehensive EMS Data Clean & Seed using image_archive =="))

        with transaction.atomic():
            # 1. PRESERVE & CONFIGURE ADMIN ACCOUNTS
            self.setup_admins()

            # 2. CLEAN & SEED HALLS WITH RICH SPECS, FEATURES & GALLERY
            halls = self.setup_halls()

            # 3. CLEAN & SEED ROOMS WITH RICH SPECS & FEATURES
            rooms = self.setup_rooms()

            # 4. SEED CATALOG (Furniture, Stages, Services, Catering)
            furniture_items, stages, services, catering_packages = self.setup_catalog(halls)

            # 5. SEED VERIFIED CUSTOMERS WITH SECURE HASHED PASSWORDS
            customers = self.setup_customers()

            # 6. RESET & SEED PRODUCTION-GRADE BOOKINGS
            self.setup_bookings(customers, halls, rooms, furniture_items, stages, services, catering_packages)

            # 7. SEED GALLERY CATEGORIES, GALLERY ITEMS & PAGE HERO HEADERS
            self.setup_pages_and_gallery(halls)

        self.stdout.write(self.style.SUCCESS("== Data Clean & Seed Completed Successfully! =="))

    def setup_admins(self):
        self.stdout.write("1. Preserving & Configuring Admin Accounts...")

        # 1. Root / Developer: admin (PRESERVED)
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@royalpalace.com",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Root",
                "last_name": "Developer",
            },
        )
        if created or not admin_user.password.startswith("pbkdf2_"):
            admin_user.set_password("Admin@Royal2026!")
            admin_user.save()
        AdminProfile.objects.update_or_create(user=admin_user, defaults={"role": "developer"})

        # 2. Existing SAIF (PRESERVED)
        saif_user = User.objects.filter(username__iexact="SAIF").first()
        if saif_user:
            saif_user.is_staff = True
            saif_user.save()
            AdminProfile.objects.update_or_create(user=saif_user, defaults={"role": "admin"})

        # 3. Superadmin Account: superadmin
        super_user, s_created = User.objects.get_or_create(
            username="superadmin",
            defaults={
                "email": "superadmin@royalpalace.com",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Vikramaditya",
                "last_name": "Singhania",
            },
        )
        if s_created or not super_user.password.startswith("pbkdf2_"):
            super_user.set_password("Super@Royal2026!")
            super_user.save()
        AdminProfile.objects.update_or_create(user=super_user, defaults={"role": "superadmin"})

        # 4. Operations Event Manager (Admin): event_manager
        mgr_user, m_created = User.objects.get_or_create(
            username="event_manager",
            defaults={
                "email": "manager@royalpalace.com",
                "is_staff": True,
                "is_superuser": False,
                "first_name": "Rajesh",
                "last_name": "Khanna",
            },
        )
        if m_created or not mgr_user.password.startswith("pbkdf2_"):
            mgr_user.set_password("Manager@Royal2026!")
            mgr_user.save()
        AdminProfile.objects.update_or_create(user=mgr_user, defaults={"role": "admin"})

    def setup_halls(self):
        self.stdout.write("2. Cleaning & Seeding Halls with Rich Details & image_archive Media...")

        # Purge legacy dummy halls with typos/test values
        legacy_slugs = ["royal-place", "diamond-banquet", "gardan-premium", "eklavya-banquet-updated", "dj-hall"]
        Hall.objects.filter(slug__in=legacy_slugs).delete()

        halls_data = [
            {
                "name": "Royal Kohinoor Grand Ballroom",
                "slug": "royal-kohinoor-ballroom",
                "capacity": 800,
                "price": Decimal("250000.00"),
                "location": "North Wing, Level 1",
                "parking_capacity": 250,
                "description": "Our flagship grand ballroom featuring Bohemian crystal chandeliers, soaring ceilings, acoustic sound insulation, and an expansive stage area for royal weddings and international summits.",
                "image": "image_archive/fernando-alvarez-rodriguez-M7GddPqJowg-unsplash.jpg",
                "banner_image": "image_archive/fernando-alvarez-rodriguez-M7GddPqJowg-unsplash.jpg",
                "is_ac": True,
                "is_wifi": True,
                "is_featured": True,
                "show_badge": True,
                "gallery_images": [
                    "image_archive/visualsofdana-T5pL6ciEn-I-unsplash.jpg",
                    "image_archive/runnyrem-LfqmND-hym8-unsplash.jpg",
                ],
                "features": [
                    ("fa-solid fa-snowflake", "Central Air Conditioning", "High-capacity multi-zone climate control", 1),
                    ("fa-solid fa-wifi", "High-Speed Wi-Fi 6", "Dedicated gigabit connectivity throughout", 2),
                    ("fa-solid fa-square-parking", "Valet Parking Available", "250+ reserved underground vehicle bays", 3),
                    ("fa-solid fa-users", "800 Guest Capacity", "Spacious banquet seating and aisle layout", 4),
                    ("fa-solid fa-music", "Concert-Grade Acoustics", "JBL surround line-array audio setup", 5),
                    ("fa-solid fa-lightbulb", "Intelligent Stage Lighting", "Motorized RGB beam and wash luminaires", 6),
                ],
            },
            {
                "name": "Imperial Crystal Palace Hall",
                "slug": "imperial-crystal-hall",
                "capacity": 500,
                "price": Decimal("180000.00"),
                "location": "East Wing, Ground Floor",
                "parking_capacity": 180,
                "description": "Contemporary glass architecture offering double-height panoramic garden views, dynamic LED wash lighting, and dedicated VIP hospitality lounges.",
                "image": "image_archive/point3d-commercial-imaging-ltd-oxeCZrodz78-unsplash.jpg",
                "banner_image": "image_archive/point3d-commercial-imaging-ltd-oxeCZrodz78-unsplash.jpg",
                "is_ac": True,
                "is_wifi": True,
                "is_featured": True,
                "show_badge": True,
                "gallery_images": [
                    "image_archive/linus-mimietz-p3UWyaujtQo-unsplash.jpg",
                    "image_archive/bilderboken-rlwE8f8anOc-unsplash.jpg",
                ],
                "features": [
                    ("fa-solid fa-snowflake", "Climate Controlled", "Independent airflow regulation", 1),
                    ("fa-solid fa-gem", "Panoramic Glass Facade", "Direct natural lighting & sunset garden views", 2),
                    ("fa-solid fa-square-parking", "Dedicated VIP Parking", "180 secure parking slots", 3),
                    ("fa-solid fa-champagne-glasses", "Integrated Cocktail Lounge", "Built-in marble beverage counter", 4),
                ],
            },
            {
                "name": "Heritage Regal Pavilion",
                "slug": "heritage-regal-pavilion",
                "capacity": 350,
                "price": Decimal("120000.00"),
                "location": "Heritage Courtyard",
                "parking_capacity": 120,
                "description": "Traditional Rajasthani stone jharokhas, handcrafted wooden motifs, and intimate acoustic ambiance for traditional ceremonies and engagements.",
                "image": "image_archive/vojtech-bruzek-Yrxr3bsPdS0-unsplash.jpg",
                "banner_image": "image_archive/vojtech-bruzek-Yrxr3bsPdS0-unsplash.jpg",
                "is_ac": True,
                "is_wifi": True,
                "is_featured": False,
                "show_badge": False,
                "gallery_images": [
                    "image_archive/christian-lambert-vmIWr0NnpCQ-unsplash.jpg",
                ],
                "features": [
                    ("fa-solid fa-archway", "Artisanal Heritage Arches", "Hand-carved sandstone pillars", 1),
                    ("fa-solid fa-snowflake", "Concealed AC Ducts", "Silent split-duct cooling system", 2),
                    ("fa-solid fa-sun", "Open Courtyard Access", "Direct flow to royal fountain garden", 3),
                ],
            },
            {
                "name": "Emerald Garden Lawn & Banquet",
                "slug": "emerald-garden-lawn",
                "capacity": 650,
                "price": Decimal("150000.00"),
                "location": "Outdoor South Gardens",
                "parking_capacity": 200,
                "description": "Expansive lush green lawn with illuminated palm avenues, waterfall backdrops, and open-air luxury cabanas for sangeet and reception nights.",
                "image": "image_archive/valeriia-bugaiova-_pPHgeHz1uk-unsplash.jpg",
                "banner_image": "image_archive/valeriia-bugaiova-_pPHgeHz1uk-unsplash.jpg",
                "is_ac": False,
                "is_wifi": True,
                "is_featured": True,
                "show_badge": True,
                "gallery_images": [
                    "image_archive/gerson-repreza-CepDpEiALqM-unsplash.jpg",
                ],
                "features": [
                    ("fa-solid fa-tree", "Lush Carpet Lawn", "15,000 sq. ft. manicured natural turf", 1),
                    ("fa-solid fa-cloud-moon", "Fairytale Fairy Lighting", "Illuminated palm tree canopy", 2),
                    ("fa-solid fa-shield-halved", "All-Weather Pergolas", "Waterproof semi-covered cabanas", 3),
                ],
            },
        ]

        halls = []
        for hd in halls_data:
            features = hd.pop("features")
            gallery_imgs = hd.pop("gallery_images", [])
            hall, _ = Hall.objects.update_or_create(slug=hd["slug"], defaults=hd)
            halls.append(hall)

            # Re-seed features
            hall.features.all().delete()
            for icon, title, subtitle, order in features:
                HallFeature.objects.create(
                    hall=hall,
                    icon=icon,
                    title=title,
                    subtitle=subtitle,
                    order=order,
                )

            # Re-seed hall gallery
            hall.gallery.all().delete()
            for g_img in gallery_imgs:
                HallGallery.objects.create(hall=hall, hall_image=g_img)

        return halls

    def setup_rooms(self):
        self.stdout.write("3. Cleaning & Seeding Rooms with image_archive Media...")

        # Purge legacy dummy rooms
        Room.objects.filter(name__in=["Parent", "meeting Room  ", "Non-Ac", "AC Room", "Groom Suite", "Bridal Suite", "Family Room"]).delete()
        Room.objects.filter(name__icontains="meeting").delete()

        rooms_data = [
            {
                "name": "Presidential Luxury Suite",
                "price": Decimal("12000.00"),
                "capacity": 2,
                "total_rooms": 4,
                "image": "image_archive/roberto-nickson-emqnSQwQQDo-unsplash.jpg",
                "description": "Master king suite featuring panoramic balcony views, jacuzzi bath, plush Italian furnishings, and 24/7 dedicated butler service.",
                "features": ["King Size Plush Bed", "Jacuzzi & Designer Bath", "Private Scenic Balcony", "Central AC & Heating", "High-Speed Wi-Fi", "Mini Bar & Espresso Station"],
            },
            {
                "name": "Bridal VIP Preparation Suite",
                "price": Decimal("15000.00"),
                "capacity": 4,
                "total_rooms": 2,
                "image": "image_archive/sasha-kaunas-TAgGZWz6Qg8-unsplash.jpg",
                "description": "Spacious styling suite with professional 360-degree vanity mirrors, makeup stations, steamer wardrobe, and direct private access to the grand stage.",
                "features": ["Salon Makeup Station", "Full-Length Vanity Mirrors", "Garment Steamer & Wardrobe", "Attached Luxury Washroom", "Direct Stage Access", "Central Air Conditioning"],
            },
            {
                "name": "Executive Deluxe Suite",
                "price": Decimal("7500.00"),
                "capacity": 2,
                "total_rooms": 14,
                "image": "image_archive/sasha-kaunas-67-sOi7mVIk-unsplash.jpg",
                "description": "Contemporary executive accommodation with plush queen bedding, ergonomic work desk, smart TV, and garden views.",
                "features": ["Plush Queen Bed", "En-suite Modern Bathroom", "Smart 55-inch LED TV", "Work Desk & Ergonomic Chair", "Complimentary Wi-Fi", "24/7 In-Room Dining"],
            },
            {
                "name": "Family Celebration Suite",
                "price": Decimal("9000.00"),
                "capacity": 5,
                "total_rooms": 6,
                "image": "image_archive/sasha-kaunas-xEaAoizNFV8-unsplash.jpg",
                "description": "Spacious dual-bedroom family suite ideal for immediate family and wedding parties, featuring a shared lounge and dining space.",
                "features": ["Dual Interconnected Bedrooms", "Living & Dining Lounge", "2 Attached Bathrooms", "Climate Control", "Wi-Fi Access", "Tea/Coffee Maker"],
            },
            {
                "name": "Standard Guest Accommodation",
                "price": Decimal("4500.00"),
                "capacity": 2,
                "total_rooms": 25,
                "image": "image_archive/francesca-saraco-_dS27XGgRyQ-unsplash.jpg",
                "description": "Comfortable, climate-controlled guest rooms for traveling event attendees with all essential amenities.",
                "features": ["Twin / Queen Bedding", "Attached Washroom", "AC", "High-Speed Internet", "Daily Housekeeping Service"],
            },
        ]

        rooms = []
        for rd in rooms_data:
            features = rd.pop("features")
            room, _ = Room.objects.update_or_create(name=rd["name"], defaults=rd)
            rooms.append(room)

            # Re-seed features
            room.features.all().delete()
            for fname in features:
                RoomFeature.objects.create(room=room, name=fname)

        return rooms

    def setup_catalog(self, halls):
        self.stdout.write("4. Seeding Catalog (Furniture, Stages, Services, Catering)...")

        # FURNITURE
        furniture_items = []
        for hall in halls:
            fcat, _ = FurnitureCategory.objects.get_or_create(hall=hall, name="Banquet Seating & Tables")
            items = [
                {"name": "Golden Chiavari Chairs with Velvet Cushions", "price": Decimal("250.00"), "unit": "piece"},
                {"name": "Round 10-Seater Banquet Tables with Silk Linen", "price": Decimal("850.00"), "unit": "table"},
                {"name": "Royal Maharaja Velvet Twin Sofa", "price": Decimal("5000.00"), "unit": "set"},
                {"name": "Illuminated High-Top Cocktail Bar Stools", "price": Decimal("400.00"), "unit": "piece"},
            ]
            for it in items:
                fitem, _ = FurnitureItem.objects.update_or_create(
                    category=fcat,
                    name=it["name"],
                    defaults={"price": it["price"], "unit": it["unit"], "max_quantity": 500}
                )
                furniture_items.append(fitem)

        # STAGE DESIGNS
        stages = []
        for hall in halls:
            scat, _ = StageCategory.objects.get_or_create(hall=hall, name="Grand Wedding & Gala Stages")
            stage_items = [
                {"name": "Royal Kohinoor Floral Mandap & Stage", "price": Decimal("65000.00"), "badge": "Signature", "image": "image_archive/frames-for-your-heart-zSG-kd-L6vw-unsplash.jpg"},
                {"name": "Modern Crystal & LED Infinity Stage", "price": Decimal("85000.00"), "badge": "Trending", "image": "image_archive/bilderboken-rlwE8f8anOc-unsplash.jpg"},
                {"name": "Traditional Marigold & Brass Heritage Stage", "price": Decimal("45000.00"), "badge": "Classic", "image": "image_archive/christian-lambert-vmIWr0NnpCQ-unsplash.jpg"},
            ]
            for st in stage_items:
                stage_obj, _ = StageDesign.objects.update_or_create(
                    category=scat,
                    name=st["name"],
                    defaults={"price": st["price"], "badge": st["badge"], "image": st["image"]}
                )
                stages.append(stage_obj)

        # SERVICES
        services = []
        for hall in halls:
            srv_cat, _ = ServiceCategory.objects.get_or_create(hall=hall, name="Production & Media Services")
            service_items = [
                {"name": "Cinematic 4K Drone & 3-Camera Live Stream", "price": Decimal("45000.00")},
                {"name": "Traditional Shehnai & Classical Orchestra Ensemble", "price": Decimal("30000.00")},
                {"name": "Intelligent Robotic Moving-Head Stage Lighting", "price": Decimal("35000.00")},
                {"name": "VIP Valet Parking & Concierge Fleet Team", "price": Decimal("20000.00")},
            ]
            for s in service_items:
                srv_obj, _ = Service.objects.update_or_create(
                    category=srv_cat,
                    name=s["name"],
                    defaults={"price": s["price"]}
                )
                services.append(srv_obj)

        # CATERING PACKAGES
        catering_data = [
            {"name": "Royal Shahi Feast (Platinum Menu)", "slug": "royal-shahi-platinum", "price": Decimal("1850.00"), "image": "image_archive/manuel-moreno-DGa0LQ0yDPc-unsplash.jpg", "description": "7-course live gourmet dining with imported mocktail bar, artisanal kebabs, and dessert boutique."},
            {"name": "Grand Imperial Buffet (Gold Menu)", "slug": "grand-imperial-gold", "price": Decimal("1450.00"), "image": "image_archive/rhema-kallianpur-uocSnWMhnAs-unsplash.jpg", "description": "5-course lavish spread spanning Mughlai, Pan-Asian, Continental, and traditional Indian live counters."},
            {"name": "Regal Celebration Spread (Silver Menu)", "slug": "regal-silver-spread", "price": Decimal("1150.00"), "image": "image_archive/sara-dubler-Koei_7yYtIo-unsplash.jpg", "description": "Standard banquet buffet featuring welcome drinks, appetizers, multi-cuisine main course, and sweets."},
        ]
        catering_packages = []
        for cd in catering_data:
            pkg, _ = CateringPackage.objects.update_or_create(slug=cd["slug"], defaults=cd)
            catering_packages.append(pkg)

            sec, _ = MenuSection.objects.get_or_create(package=pkg, title="Appetizers & Starters", defaults={"order": 1})
            cat, _ = MenuCategory.objects.get_or_create(section=sec, title="Live Kebabs & Bites", defaults={"order": 1})
            MenuItem.objects.get_or_create(section=cat, name="Paneer Tikka Angara", defaults={"is_available": True})
            MenuItem.objects.get_or_create(section=cat, name="Dahi Ke Kebab", defaults={"is_available": True})

            sec2, _ = MenuSection.objects.get_or_create(package=pkg, title="Royal Main Course", defaults={"order": 2})
            cat2, _ = MenuCategory.objects.get_or_create(section=sec2, title="Curries & Breads", defaults={"order": 1})
            MenuItem.objects.get_or_create(section=cat2, name="Paneer Lababdar", defaults={"is_available": True})
            MenuItem.objects.get_or_create(section=cat2, name="Dal Makhani Bukhara", defaults={"is_available": True})
            MenuItem.objects.get_or_create(section=cat2, name="Kashmiri Dum Pulao", defaults={"is_available": True})

            sec3, _ = MenuSection.objects.get_or_create(package=pkg, title="Dessert Boutique", defaults={"order": 3})
            cat3, _ = MenuCategory.objects.get_or_create(section=sec3, title="Sweet Delights", defaults={"order": 1})
            MenuItem.objects.get_or_create(section=cat3, name="Shahi Tukda with Rabri", defaults={"is_available": True})
            MenuItem.objects.get_or_create(section=cat3, name="Kesari Jalebi with Live Counter", defaults={"is_available": True})

        return furniture_items, stages, services, catering_packages

    def setup_customers(self):
        self.stdout.write("5. Seeding Verified Customer Accounts with Hashed Passwords...")

        # Purge legacy dummy customer records without bookings
        Customer.objects.filter(name__in=["RRR", "Deliverable Test Customer", "Test New Customer"]).delete()

        customer_profiles_data = [
            {
                "username": "rohit_sharma",
                "name": "Rohit Sharma",
                "email": "rohit.sharma@example.com",
                "phone": "9876543210",
                "address": "Flat 402, Sea Green Heights, Worli, Mumbai",
            },
            {
                "username": "priya_patel",
                "name": "Priya Patel",
                "email": "priya.patel@example.com",
                "phone": "9812345678",
                "address": "Villa 12, Palm Meadows, Whitefield, Bangalore",
            },
            {
                "username": "vikram_mehta",
                "name": "Vikram Mehta",
                "email": "vikram.mehta@example.com",
                "phone": "9823456789",
                "address": "A-15, Civil Lines, Jaipur, Rajasthan",
            },
            {
                "username": "ananya_singh",
                "name": "Ananya Singh",
                "email": "ananya.singh@example.com",
                "phone": "9834567890",
                "address": "Tower 3, Sector 62, Golf Course Road, Gurgaon",
            },
            {
                "username": "kavita_reddy",
                "name": "Kavita Reddy",
                "email": "kavita.reddy@example.com",
                "phone": "9845678901",
                "address": "Road No. 36, Jubilee Hills, Hyderabad",
            },
            {
                "username": "arjun_kapoor",
                "name": "Arjun Kapoor",
                "email": "arjun.kapoor@example.com",
                "phone": "9856789012",
                "address": "Bungalow 7, Queens Park, Alipore, Kolkata",
            },
        ]

        customers = []
        for cd in customer_profiles_data:
            user, _ = User.objects.get_or_create(
                username=cd["username"],
                defaults={
                    "email": cd["email"],
                    "first_name": cd["name"].split()[0],
                    "last_name": cd["name"].split()[-1] if len(cd["name"].split()) > 1 else "",
                },
            )
            # Secure PBKDF2 Password Hashing
            user.set_password("Client@2026!")
            user.save()

            customer, _ = Customer.objects.update_or_create(
                phone=cd["phone"],
                defaults={
                    "user": user,
                    "name": cd["name"],
                    "email": cd["email"],
                    "address": cd["address"],
                },
            )
            customers.append(customer)

        return customers

    def setup_bookings(self, customers, halls, rooms, furniture_items, stages, services, catering_packages):
        self.stdout.write("6. Resetting & Seeding Live Bookings...")

        Booking.objects.all().delete()
        today = date.today()

        bookings_plan = [
            {
                "customer": customers[0],
                "event_type": "Grand Wedding Ceremony",
                "event_date": today + timedelta(days=21),
                "status": "confirmed",
                "total_guest": 450,
                "hall": halls[0],
                "rooms": [(rooms[0], 2), (rooms[1], 1), (rooms[2], 4)],
                "stage": stages[0],
                "furniture": [(furniture_items[0], 250), (furniture_items[1], 25)],
                "services": [services[0], services[2]],
                "catering": catering_packages[0],
            },
            {
                "customer": customers[1],
                "event_type": "Royal Sangeet & Cocktail Night",
                "event_date": today + timedelta(days=14),
                "status": "confirmed",
                "total_guest": 300,
                "hall": halls[1],
                "rooms": [(rooms[2], 3), (rooms[4], 5)],
                "stage": stages[1],
                "furniture": [(furniture_items[0], 150), (furniture_items[3], 20)],
                "services": [services[0], services[1], services[3]],
                "catering": catering_packages[1],
            },
            {
                "customer": customers[2],
                "event_type": "Corporate Annual Leadership Summit",
                "event_date": today + timedelta(days=7),
                "status": "confirmed",
                "total_guest": 250,
                "hall": halls[1],
                "rooms": [(rooms[0], 1), (rooms[2], 5)],
                "stage": stages[1],
                "furniture": [(furniture_items[0], 200), (furniture_items[1], 20)],
                "services": [services[0], services[2]],
                "catering": catering_packages[1],
            },
            {
                "customer": customers[3],
                "event_type": "Traditional Engagement & Ring Ceremony",
                "event_date": today + timedelta(days=35),
                "status": "pending",
                "total_guest": 200,
                "hall": halls[2],
                "rooms": [(rooms[2], 2), (rooms[1], 1)],
                "stage": stages[2],
                "furniture": [(furniture_items[0], 120), (furniture_items[1], 15)],
                "services": [services[1]],
                "catering": catering_packages[2],
            },
            {
                "customer": customers[4],
                "event_type": "Destination Wedding Reception",
                "event_date": today + timedelta(days=45),
                "status": "pending",
                "total_guest": 500,
                "hall": halls[3],
                "rooms": [(rooms[0], 2), (rooms[2], 6), (rooms[1], 1)],
                "stage": stages[0],
                "furniture": [(furniture_items[0], 300), (furniture_items[1], 30)],
                "services": [services[0], services[2], services[3]],
                "catering": catering_packages[0],
            },
            {
                "customer": customers[5],
                "event_type": "Luxury Golden Jubilee Celebration",
                "event_date": today + timedelta(days=10),
                "status": "confirmed",
                "total_guest": 180,
                "hall": halls[2],
                "rooms": [(rooms[0], 1), (rooms[2], 2)],
                "stage": stages[2],
                "furniture": [(furniture_items[0], 100), (furniture_items[1], 12)],
                "services": [services[1], services[3]],
                "catering": catering_packages[1],
            },
            {
                "customer": customers[0],
                "event_type": "Executive Product Launch & Media Gala",
                "event_date": today - timedelta(days=5),
                "status": "confirmed",
                "total_guest": 350,
                "hall": halls[0],
                "rooms": [(rooms[0], 2), (rooms[2], 4)],
                "stage": stages[1],
                "furniture": [(furniture_items[0], 200), (furniture_items[1], 20)],
                "services": [services[0], services[2]],
                "catering": catering_packages[0],
            },
            {
                "customer": customers[1],
                "event_type": "Birthday Anniversary Banquet",
                "event_date": today - timedelta(days=12),
                "status": "cancelled",
                "total_guest": 150,
                "hall": halls[2],
                "rooms": [(rooms[2], 2)],
                "stage": stages[2],
                "furniture": [(furniture_items[0], 80), (furniture_items[1], 10)],
                "services": [services[1]],
                "catering": catering_packages[2],
            },
        ]

        for bp in bookings_plan:
            booking = Booking.objects.create(
                customer=bp["customer"],
                event_type=bp["event_type"],
                event_date=bp["event_date"],
                status=bp["status"],
                total_guest=bp["total_guest"],
            )

            total_amount = Decimal("0.00")

            # Hall
            hall_price = bp["hall"].price
            BookingHall.objects.create(booking=booking, hall=bp["hall"], price=hall_price)
            total_amount += hall_price

            # Rooms
            for rm, qty in bp["rooms"]:
                subtotal = rm.price * qty
                BookingRoom.objects.create(booking=booking, room=rm, quantity=qty, price=rm.price, subtotal=subtotal)
                total_amount += subtotal

            # Stage
            st_price = bp["stage"].price
            BookingStage.objects.create(booking=booking, stage=bp["stage"], price=st_price)
            total_amount += st_price

            # Furniture
            for f_item, qty in bp["furniture"]:
                subtotal = f_item.price * qty
                BookingFurniture.objects.create(booking=booking, furniture=f_item, quantity=qty, price=f_item.price, subtotal=subtotal)
                total_amount += subtotal

            # Services
            for srv in bp["services"]:
                BookingService.objects.create(booking=booking, service=srv, price=srv.price)
                total_amount += srv.price

            # Catering
            cat_pkg = bp["catering"]
            cat_total = cat_pkg.price * bp["total_guest"]
            bc = BookingCatering.objects.create(
                booking=booking,
                package=cat_pkg,
                guest_count=bp["total_guest"],
                price_per_plate=cat_pkg.price,
                total_price=cat_total,
            )
            total_amount += cat_total

            # Menu Items
            for sec in cat_pkg.sections.all():
                for cat_group in sec.categories.all():
                    for mi in cat_group.items.filter(is_available=True):
                        BookingMenuItem.objects.create(
                            booking_catering=bc,
                            section=sec.title,
                            item_name=mi.name,
                        )

            booking.total_amount = total_amount
            booking.save(update_fields=["total_amount"])

    def setup_pages_and_gallery(self, halls):
        self.stdout.write("7. Configuring Page Hero Headers & Seeding Gallery from image_archive...")

        # Home Page Hero
        hp = HomePage.objects.first()
        if not hp:
            hp = HomePage.objects.create(
                hero_title="Experience Royal Luxury & Grandeur",
                hero_description="Discover landmark ballrooms, bespoke culinary art, and luxury hospitality tailored for your royal moments.",
                hero_image="image_archive/fernando-alvarez-rodriguez-M7GddPqJowg-unsplash.jpg",
            )
        else:
            hp.hero_image = "image_archive/fernando-alvarez-rodriguez-M7GddPqJowg-unsplash.jpg"
            hp.save()

        # Room Page Hero
        RoomPage.objects.update_or_create(
            id=1,
            defaults={
                "hero_title": "Luxury Guest Accommodations",
                "hero_subtitle": "Experience royal hospitality, private suites, and world-class luxury stays for your guests.",
                "hero_image": "image_archive/roberto-nickson-emqnSQwQQDo-unsplash.jpg",
            },
        )

        # Hall Page Hero
        HallPage.objects.update_or_create(
            id=1,
            defaults={
                "hero_title": "Grand Venues & Royal Palaces",
                "hero_subtitle": "Discover architectural splendor, lush garden banquets, and world-class ballrooms for your landmark moments.",
                "hero_image": "image_archive/point3d-commercial-imaging-ltd-oxeCZrodz78-unsplash.jpg",
            },
        )

        # Catering Page Hero
        CateringPage.objects.update_or_create(
            id=1,
            defaults={
                "hero_title": "Royal Culinary & Banquet Menus",
                "hero_subtitle": "Multi-cuisine live stations, artisanal appetizers, and gourmet dessert spreads.",
                "hero_image": "image_archive/manuel-moreno-DGa0LQ0yDPc-unsplash.jpg",
            },
        )

        # Gallery Categories & Items
        cats_data = [
            {
                "name": "Royal Weddings",
                "slug": "royal-weddings",
                "images": [
                    ("A Royal Wedding Ceremony", "image_archive/alev-takil-lw3Lqe2K7xc-unsplash.jpg"),
                    ("Grand Mandap & Floral Decor", "image_archive/frames-for-your-heart-zSG-kd-L6vw-unsplash.jpg"),
                ],
            },
            {
                "name": "Grand Receptions",
                "slug": "grand-receptions",
                "images": [
                    ("Ballroom Evening Reception", "image_archive/runnyrem-LfqmND-hym8-unsplash.jpg"),
                    ("Crystal Palace Ambiance", "image_archive/point3d-commercial-imaging-ltd-oxeCZrodz78-unsplash.jpg"),
                ],
            },
            {
                "name": "Corporate Summits",
                "slug": "corporate-summits",
                "images": [
                    ("Modern Stage & AV Setup", "image_archive/bilderboken-rlwE8f8anOc-unsplash.jpg"),
                    ("Executive Banquet Layout", "image_archive/visualsofdana-T5pL6ciEn-I-unsplash.jpg"),
                ],
            },
            {
                "name": "Traditional Ceremonies",
                "slug": "traditional-ceremonies",
                "images": [
                    ("Heritage Courtyard Setup", "image_archive/vojtech-bruzek-Yrxr3bsPdS0-unsplash.jpg"),
                    ("Classical Architecture & Lighting", "image_archive/christian-lambert-vmIWr0NnpCQ-unsplash.jpg"),
                ],
            },
            {
                "name": "Lawn & Garden Galas",
                "slug": "lawn-garden-galas",
                "images": [
                    ("Lush Emerald Garden Venue", "image_archive/valeriia-bugaiova-_pPHgeHz1uk-unsplash.jpg"),
                    ("Sunset Outdoor Celebration", "image_archive/gerson-repreza-CepDpEiALqM-unsplash.jpg"),
                ],
            },
        ]

        GalleryItem.objects.all().delete()
        for cdata in cats_data:
            category, _ = GalleryCategory.objects.get_or_create(slug=cdata["slug"], defaults={"name": cdata["name"]})
            for title, img_path in cdata["images"]:
                GalleryItem.objects.create(category=category, title=title, image=img_path)
