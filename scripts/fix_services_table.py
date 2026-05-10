#!/usr/bin/env python
"""
Script to manually create the missing services_servicesherosettings table.
This fixes the database inconsistency where migration 0001 is marked as applied
but the ServicesHeroSettings table was never created.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
django.setup()

from django.db import connection
from services.models import ServicesHeroSettings

def create_services_hero_table():
    """Create the services_servicesherosettings table manually"""
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='services_servicesherosettings';
        """)
        
        if cursor.fetchone():
            print("✓ Table 'services_servicesherosettings' already exists")
            return True
        
        print("Creating 'services_servicesherosettings' table...")
        
        # Create the table based on the model definition
        cursor.execute("""
            CREATE TABLE "services_servicesherosettings" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "subtitle" varchar(300) NOT NULL,
                "background_image" varchar(100) NULL,
                "background_url" varchar(500) NOT NULL,
                "is_active" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            );
        """)
        
        print("✓ Table 'services_servicesherosettings' created successfully")
        
        # Insert default record
        cursor.execute("""
            INSERT INTO "services_servicesherosettings" 
            (title, subtitle, background_url, is_active, created_at, updated_at)
            VALUES (
                'Our Services',
                'Comprehensive Real Estate Solutions',
                'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
                1,
                datetime('now'),
                datetime('now')
            );
        """)
        
        print("✓ Default record inserted")
        
        return True

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("Fixing services_servicesherosettings table")
        print("=" * 60)
        
        if create_services_hero_table():
            print("\n✓ SUCCESS: Table created and ready for migrations")
            print("\nNext steps:")
            print("1. Run: python manage.py migrate services")
            print("2. Start containers: docker compose up -d")
        else:
            print("\n✗ FAILED: Could not create table")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
