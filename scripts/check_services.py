#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
django.setup()

from services.models import Service, ServiceFeature, ServicesHeroSettings

print("=== Checking Services ===")
try:
    services = Service.objects.all()
    print(f"Total services: {services.count()}")
    for service in services:
        print(f"  - {service.title} (ID: {service.id})")
        features = service.features.all()
        print(f"    Features: {features.count()}")
        for feature in features:
            print(f"      * {feature.text}")
except Exception as e:
    print(f"ERROR querying services: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Checking Hero Settings ===")
try:
    hero = ServicesHeroSettings.objects.all()
    print(f"Total hero settings: {hero.count()}")
    for h in hero:
        print(f"  - {h.title}")
except Exception as e:
    print(f"ERROR querying hero settings: {e}")
    import traceback
    traceback.print_exc()
