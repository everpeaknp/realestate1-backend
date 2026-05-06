#!/usr/bin/env python
"""
Script to find and fix missing image references in the database.
This script checks all models with ImageField and updates broken paths.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from django.db import models

def find_similar_file(broken_path):
    """Find a similar file that actually exists."""
    if not broken_path:
        return None
    
    # Get the directory and base filename
    dir_path = os.path.dirname(broken_path)
    filename = os.path.basename(broken_path)
    
    # Remove Django's unique suffix (e.g., _L0O3T7Q)
    base_name = filename.rsplit('_', 1)[0] if '_' in filename else filename.split('.')[0]
    extension = os.path.splitext(filename)[1]
    
    # Check if base file exists
    base_file = f"{base_name}{extension}"
    base_path = os.path.join(dir_path, base_file)
    full_path = os.path.join(settings.MEDIA_ROOT, base_path)
    
    if os.path.exists(full_path):
        return base_path
    
    # Try to find any file with similar name in the directory
    full_dir = os.path.join(settings.MEDIA_ROOT, dir_path)
    if os.path.exists(full_dir):
        for file in os.listdir(full_dir):
            if file.startswith(base_name) and file.endswith(extension):
                return os.path.join(dir_path, file)
    
    return None

def check_and_fix_images():
    """Check all models for broken image references and fix them."""
    fixed_count = 0
    broken_count = 0
    
    print("=" * 80)
    print("CHECKING ALL IMAGE FIELDS IN DATABASE")
    print("=" * 80)
    
    # Get all models
    for model in apps.get_models():
        # Find all ImageField fields in the model
        image_fields = [
            field for field in model._meta.get_fields()
            if isinstance(field, models.ImageField)
        ]
        
        if not image_fields:
            continue
        
        print(f"\n📋 Checking {model.__name__}...")
        
        # Check each instance
        for instance in model.objects.all():
            for field in image_fields:
                field_name = field.name
                image_field = getattr(instance, field_name)
                
                if not image_field:
                    continue
                
                image_path = str(image_field)
                full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                
                if not os.path.exists(full_path):
                    print(f"  ❌ BROKEN: {model.__name__}.{field_name} = {image_path}")
                    broken_count += 1
                    
                    # Try to find a similar file
                    fixed_path = find_similar_file(image_path)
                    
                    if fixed_path:
                        print(f"     ✅ FIXED: {fixed_path}")
                        setattr(instance, field_name, fixed_path)
                        instance.save()
                        fixed_count += 1
                    else:
                        print(f"     ⚠️  NO FIX FOUND")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Found {broken_count} broken images, fixed {fixed_count}")
    print("=" * 80)

if __name__ == '__main__':
    check_and_fix_images()
