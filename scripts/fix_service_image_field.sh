#!/bin/bash
cd /opt/stacks/realestate1
docker compose run --rm realestate1-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db.sqlite3')
cursor = conn.cursor()

print('Fixing services_service.image field to allow NULL...')

# SQLite doesn't support ALTER COLUMN directly, so we need to:
# 1. Create a new table with correct schema
# 2. Copy data
# 3. Drop old table
# 4. Rename new table

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
        image_url VARCHAR(500) NOT NULL
    )
''')

# Copy data from old table to new table
cursor.execute('''
    INSERT INTO services_service_new 
    SELECT id, title, slug, description, image, layout, phone, email, 
           button_text, is_active, \"order\", created_at, updated_at, image_url
    FROM services_service
''')

# Drop old table
cursor.execute('DROP TABLE services_service')

# Rename new table
cursor.execute('ALTER TABLE services_service_new RENAME TO services_service')

conn.commit()
print('SUCCESS: services_service.image field now allows NULL')

# Verify
cursor.execute('PRAGMA table_info(services_service)')
print('\nUpdated schema:')
for row in cursor.fetchall():
    print(row)

conn.close()
"
