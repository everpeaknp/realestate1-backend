#!/bin/bash
cd /opt/stacks/realestate1
docker compose run --rm realestate1-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db.sqlite3')
cursor = conn.cursor()

print('Fixing services_service table schema...')

# Get current columns
cursor.execute('PRAGMA table_info(services_service)')
columns = cursor.fetchall()
print('Current columns:')
for col in columns:
    print(f'  {col[1]}: {col[2]} (NULL={col[3]==0})')

# Check if image_url exists
has_image_url = any(col[1] == 'image_url' for col in columns)
print(f'\nHas image_url column: {has_image_url}')

# Create new table with correct schema
cursor.execute('''
    CREATE TABLE services_service_new (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        slug VARCHAR(200) NOT NULL UNIQUE,
        description TEXT NOT NULL,
        image VARCHAR(100) NULL,
        layout VARCHAR(20) NOT NULL,
        phone VARCHAR(50) NOT NULL,
        email VARCHAR(254) NOT NULL,
        button_text VARCHAR(100) NOT NULL,
        is_active BOOLEAN NOT NULL,
        \"order\" INTEGER NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        image_url VARCHAR(500) NOT NULL DEFAULT ''
    )
''')

# Copy data - handle both cases (with and without image_url)
if has_image_url:
    cursor.execute('''
        INSERT INTO services_service_new 
        SELECT id, title, slug, description, image, layout, phone, email, 
               button_text, is_active, \"order\", created_at, updated_at, image_url
        FROM services_service
    ''')
else:
    cursor.execute('''
        INSERT INTO services_service_new 
        (id, title, slug, description, image, layout, phone, email, 
         button_text, is_active, \"order\", created_at, updated_at, image_url)
        SELECT id, title, slug, description, image, layout, phone, email, 
               button_text, is_active, \"order\", created_at, updated_at, ''
        FROM services_service
    ''')

# Drop old table
cursor.execute('DROP TABLE services_service')

# Rename new table
cursor.execute('ALTER TABLE services_service_new RENAME TO services_service')

conn.commit()
print('\nSUCCESS: services_service table schema fixed')

# Verify
cursor.execute('PRAGMA table_info(services_service)')
print('\nUpdated schema:')
for row in cursor.fetchall():
    print(f'  {row[1]}: {row[2]} (NULL={row[3]==0})')

conn.close()
"
