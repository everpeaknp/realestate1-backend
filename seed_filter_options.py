"""Seed filter option data for the new structured FilterOption model"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from properties.models import PropertiesHeroSettings, FilterOption

s, _ = PropertiesHeroSettings.objects.get_or_create(pk=1)

# Clear existing options to avoid duplicates during re-seeding
FilterOption.objects.filter(hero_settings=s).delete()

data = {
    'PROPERTY_TYPE': [
        ("HOUSE", "House"),
        ("APARTMENT", "Apartment"),
        ("UNIT", "Unit"),
        ("TOWNHOUSE", "Townhouse"),
        ("VILLA", "Villa"),
        ("LAND", "Land"),
    ],
    'MIN_PRICE': [
        ("100000", "$100K"),
        ("200000", "$200K"),
        ("300000", "$300K"),
        ("400000", "$400K"),
        ("500000", "$500K"),
        ("750000", "$750K"),
        ("1000000", "$1M"),
    ],
    'MAX_PRICE': [
        ("200000", "$200K"),
        ("300000", "$300K"),
        ("400000", "$400K"),
        ("500000", "$500K"),
        ("750000", "$750K"),
        ("1000000", "$1M"),
        ("2000000", "$2M"),
    ],
    'BEDROOMS': [
        ("1", "1+"),
        ("2", "2+"),
        ("3", "3+"),
        ("4", "4+"),
        ("5", "5+"),
    ],
    'STATUS': [
        ("CURRENT", "Current"),
        ("ACTIVE", "Active"),
        ("SOLD", "Sold"),
        ("LEASED", "Leased"),
        ("PENDING", "Pending"),
    ]
}

created_count = 0
for category, options in data.items():
    for i, (value, label) in enumerate(options):
        FilterOption.objects.create(
            hero_settings=s,
            category=category,
            value=value,
            label=label,
            order=i * 10
        )
        created_count += 1

print(f"Successfully seeded {created_count} filter options!")
