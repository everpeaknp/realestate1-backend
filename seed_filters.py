"""Seed filter configuration data for PropertiesHeroSettings"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from properties.models import PropertiesHeroSettings

s, _ = PropertiesHeroSettings.objects.get_or_create(pk=1)

s.show_filters = True
s.filter_title = "Filters"

s.property_types = [
    {"value": "HOUSE", "label": "House"},
    {"value": "APARTMENT", "label": "Apartment"},
    {"value": "UNIT", "label": "Unit"},
    {"value": "TOWNHOUSE", "label": "Townhouse"},
    {"value": "VILLA", "label": "Villa"},
    {"value": "LAND", "label": "Land"},
]

s.min_price_options = [
    {"value": "100000", "label": "\u0024100K"},
    {"value": "200000", "label": "\u0024200K"},
    {"value": "300000", "label": "\u0024300K"},
    {"value": "400000", "label": "\u0024400K"},
    {"value": "500000", "label": "\u0024500K"},
    {"value": "750000", "label": "\u0024750K"},
    {"value": "1000000", "label": "\u00241M"},
]

s.max_price_options = [
    {"value": "200000", "label": "\u0024200K"},
    {"value": "300000", "label": "\u0024300K"},
    {"value": "400000", "label": "\u0024400K"},
    {"value": "500000", "label": "\u0024500K"},
    {"value": "750000", "label": "\u0024750K"},
    {"value": "1000000", "label": "\u00241M"},
    {"value": "2000000", "label": "\u00242M"},
]

s.bedroom_options = [
    {"value": "1", "label": "1+"},
    {"value": "2", "label": "2+"},
    {"value": "3", "label": "3+"},
    {"value": "4", "label": "4+"},
    {"value": "5", "label": "5+"},
]

s.status_options = [
    {"value": "CURRENT", "label": "Current"},
    {"value": "ACTIVE", "label": "Active"},
    {"value": "SOLD", "label": "Sold"},
    {"value": "LEASED", "label": "Leased"},
    {"value": "PENDING", "label": "Pending"},
]

s.save()
print("Filter config seeded successfully!")
print("Min prices:", [o["label"] for o in s.min_price_options])
print("Max prices:", [o["label"] for o in s.max_price_options])
