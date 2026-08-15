from django.shortcuts import render,get_object_or_404
from .models import CateringPackage, CateringPage

# Create your views here.
def catering(request):
    catering_page, _ = CateringPage.objects.get_or_create(id=1)
    packages = CateringPackage.objects.filter(
        is_active=True
    )

    context = {
        'packages': packages,
        'catering_page': catering_page
    }
    return render(request, 'caterers/catering.html', context)


def package_detail(request, slug):
    package = get_object_or_404(
        CateringPackage,
        slug=slug
    )
    sections = package.sections.all().order_by(
        'order', 'id'
    )

    context = {
        'package': package,
        'sections': sections
    }

    return render(request, 'caterers/package_detail.html', context)