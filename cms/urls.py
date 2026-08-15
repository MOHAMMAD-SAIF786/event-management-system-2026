from django.urls import path
from . import views
app_name = "cms"
urlpatterns = [
    path("", views.dashboard, name="index"),
    path("login/", views.admin_login, name="admin_login"),
    path("login/alias/", views.admin_login, name="login"),
    # 2. Dashboard Route
    path("dashboard/", views.dashboard, name="dashboard"),
    # 3. Logout Route
    path("logout/", views.admin_logout, name="admin_logout"),
    path("logout/alias/", views.admin_logout, name="logout"),
        
 # BOOKINGS
    
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/add/", views.booking_add, name="booking_add"),
    path("bookings/<int:id>/", views.booking_detail, name="booking_detail"),
        
    path(
        "bookings/<int:id>/edit/",
        views.booking_edit,
        name="booking_edit",
    ),
    
    path(
        "bookings/<int:id>/delete/",
        views.booking_delete,
        name="booking_delete",
    ),
        
    path(
        "customers/",
        views.customer_list,
        name="customer_list",
    ),
        
    path(
        "customers/<int:id>/",
        views.customer_detail,
        name="customer_detail",
    ),
        
        path(
        "customers/edit/<int:id>/",
        views.customer_edit,
        name="customer_edit",
        ),
        
    path(
        "customers/delete/<int:id>/",
        views.customer_delete,
        name="customer_delete",
    ),
        
    path("halls/", views.hall_list, name="hall_list"),
        
    path("halls/<int:id>/", views.hall_detail, name="cms_hall_detail"),
        
    path("halls/<int:id>/edit/", views.hall_edit, name="hall_edit"),
        
    path("halls/add/", views.hall_add, name="hall_add"),
        
        
    path(
        "hall-feature/add/<int:hall_id>/",
        views.hall_feature_add,
        name="hall_feature_add",
    ),
    
    path(
        "hall-feature/<int:id>/edit/",
        views.hall_feature_edit,
        name="hall_feature_edit",
    ),
        
    path(
        "hall-feature/<int:id>/delete/",
        views.hall_feature_delete,
        name="hall_feature_delete",
    ),
        
    path(
        "hall-feature/save/<int:hall_id>/",
         views.hall_feature_save,
        name="hall_feature_save",
    ),
        
    path(
        "hall-gallery/save/<int:hall_id>/",
        views.hall_gallery_save,
        name="hall_gallery_save",
    ),
    
    path(
        "hall-gallery/delete/<int:id>/",
        views.hall_gallery_delete,
        name="hall_gallery_delete",
    ),
        
        # Furniture
    path(
        "furniture/add/",
        views.furniture_add,
        name="furniture_add",
    ),
    
    path(
        "furniture/save/",
        views.furniture_save,
        name="furniture_save",
    ),
    path(
        "furniture/item/add/",
        views.furniture_save,
        name="furniture_item_add",
    ),
    
    path(
        "furniture/edit/<int:id>/",
        views.furniture_edit,
        name="furniture_edit",
    ),
    path(
        "furniture/<int:id>/edit/",
        views.furniture_edit,
        name="furniture_edit_alt",
    ),
    path(
        "furniture/item/<int:id>/edit/",
        views.furniture_edit,
        name="furniture_item_edit",
    ),
    path(
        "furnitures/item/<int:id>/edit/",
        views.furniture_edit,
        name="furnitures_item_edit",
    ),
    
    path(
         "furniture/delete/<int:id>/",
        views.furniture_delete,
        name="furniture_delete",
    ),
    
    path(
        "furniture/category/add/",
        views.furniture_category_add,
        name="furniture_category_add",
    ),
    path(
        "furniture/category/delete/<int:id>/",
        views.furniture_category_delete,
        name="furniture_category_delete",
    ),
        
    path(
        "furniture/",
        views.furniture_list,
        name="furniture_list",
    ),
        
    path(
        "load-furniture-categories/",
        views.load_furniture_categories,
        name="load_furniture_categories",
    ),
        
        # STAGE DESIGN ROUTES
    path("stage-design/", views.stage_design_list, name="stage_design_list"),
        
    path("stage-design/add/", views.stage_design_add, name="stage_design_add"),
        
    path("stage-design/edit/<int:id>/", views.stage_design_edit, name="stage_design_edit"),
    path("stage-design/<int:id>/edit/", views.stage_design_edit, name="stage_design_edit_alt"),
    path("stages/<int:id>/edit/", views.stage_design_edit, name="stages_edit_alt"),
        
    path("stage-design/delete/<int:id>/", views.stage_design_delete, name="stage_design_delete"),
        
    path("stage-category/add/", views.stage_category_add, name="stage_category_add"),
        
    path("stage-category/delete/<int:id>/", views.stage_category_delete, name="stage_category_delete"),
        
    path("service-category/add/", views.service_category_add, name="service_category_add"),
        
    path("service-category/delete/<int:id>/", views.service_category_delete, name="service_category_delete"),
        
    path("service/add/", views.service_add, name="service_add"),
        
    path("service/edit/<int:id>/", views.service_edit, name="service_edit"),
        
    path("service/delete/<int:id>/", views.service_delete, name="service_delete"),
        
    path("services/", views.service_list, name="service_list"),
        
    path('rooms/', views.room_list, name='room_list'),
        
    path('rooms/add/', views.room_add, name='room_add'),
        
    path('rooms/edit/<int:room_id>/', views.room_edit, name='room_edit'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit_alt'),
    path('rooms/delete/<int:room_id>/', views.room_delete, name='room_delete'),
    path('rooms/<int:id>/toggle-status/', views.room_toggle_status, name='room_toggle_status'),
    
    path('halls/<int:id>/toggle-status/', views.hall_toggle_status, name='hall_toggle_status'),
    path('halls/<int:id>/delete/', views.hall_delete, name='hall_delete'),
    
    path('catering/', views.catering_dashboard, name='catering_list'), 
    path('caterings/', views.catering_dashboard, name='caterings_alias'), 
    path('catering/add/', views.catering_add, name='catering_add'),
    path('catering/edit/<int:package_id>/', views.catering_edit, name='catering_edit'),
    path('catering/delete/<int:package_id>/', views.catering_delete, name='catering_delete'),
    path('catering/<int:id>/toggle-status/', views.catering_toggle_status, name='catering_toggle_status'),
    path(
        "caterings/<int:pk>/detail/",
        views.package_detail_view,
        name="package_detail",
    ),

    # Catering Sub-Item Management Routes
    path("catering/section/add/<int:package_id>/", views.menu_section_add, name="menu_section_add"),
    path("catering/section/edit/<int:id>/", views.menu_section_edit, name="menu_section_edit"),
    path("catering/section/delete/<int:id>/", views.menu_section_delete, name="menu_section_delete"),
    path("catering/category/add/<int:section_id>/", views.menu_category_add, name="menu_category_add"),
    path("catering/category/delete/<int:id>/", views.menu_category_delete, name="menu_category_delete"),
    path("catering/item/add/<int:category_id>/", views.menu_item_add, name="menu_item_add"),
    path("catering/item/delete/<int:id>/", views.menu_item_delete, name="menu_item_delete"),
    path("catering/item/toggle/<int:id>/", views.menu_item_toggle, name="menu_item_toggle"),
    path("catering/pricing/add/<int:package_id>/", views.guest_pricing_add, name="guest_pricing_add"),
    path("catering/pricing/delete/<int:id>/", views.guest_pricing_delete, name="guest_pricing_delete"),
    path("catering/banner-feature/add/<int:package_id>/", views.bannar_feature_add, name="bannar_feature_add"),
    path("catering/banner-feature/add/<int:package_id>/alias/", views.bannar_feature_add, name="banner_feature_add"),
    path("catering/banner-feature/delete/<int:id>/", views.bannar_feature_delete, name="bannar_feature_delete"),
    path("catering/banner-feature/delete/<int:id>/alias/", views.bannar_feature_delete, name="banner_feature_delete"),
    path("catering/feature/add/<int:package_id>/", views.catering_feature_add, name="catering_feature_add"),
    path("catering/feature/delete/<int:id>/", views.catering_feature_delete, name="catering_feature_delete"),
    
    # Gallery Routes
    path("gallery/", views.gallery_frontend_view, name="gallery_frontend"),
    path("cms-gallery/", views.cms_gallery_view, name="gallery_dashboard"),
    
    # Permission Hierarchy Routes
    path("admin-management/", views.admin_management, name="admin_management"),
    path("developer-panel/", views.developer_panel, name="developer_panel"),
    
    path('register/', views.register_view, name='register'),
]



