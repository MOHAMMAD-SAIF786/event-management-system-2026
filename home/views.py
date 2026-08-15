from django.shortcuts import render
from .models import HomePage, Feature, ContactInfo
from rooms.models import Room
from halls.models import Hall
from catering.models import CateringPackage

def home(request):
    homepage = HomePage.objects.first()
    features = Feature.objects.all()
    contact = ContactInfo.objects.first()
    rooms = Room.objects.filter(is_active=True)[:3]
    halls = Hall.objects.filter(is_active=True)[:3]
    packages = CateringPackage.objects.filter(
        show_on_home=True,
        is_active=True
    )

    context = {
        'homepage': homepage,
        'features': features,
        'contact': contact,
        'rooms': rooms,
        'halls': halls,
        'packages': packages, 
    }
    return render(request, 'index.html', context)

def contact_view(request):
    contact = ContactInfo.objects.first()
    submitted = False
    if request.method == 'POST':
        submitted = True
    context = {
        'contact': contact,
        'submitted': submitted,
    }
    return render(request, 'contact.html', context)

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)

