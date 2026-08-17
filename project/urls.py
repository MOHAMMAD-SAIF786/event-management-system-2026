"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('logout/', user_logout, name='root_logout'),
    path('', include('home.urls')),
    path('halls/', include('halls.urls')),
    path('room/', include('rooms.urls')),
    path('catering/', include('catering.urls')),
    path('cart/', include('cart.urls')),
    path('booking/', include('booking.urls')),
    path('about_us/', include('about_us.urls')),
    path('cms/', include('cms.urls')),
]

handler404 = 'home.views.custom_404'
handler500 = 'home.views.custom_500'
handler403 = 'home.views.custom_403'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
