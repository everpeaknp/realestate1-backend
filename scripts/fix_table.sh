#!/bin/bash
cd /opt/stacks/realestate1
docker compose run --rm realestate1-backend python -c "
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/app/db.sqlite3')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS services_servicesherosettings (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        subtitle VARCHAR(300) NOT NULL,
        background_image VARCHAR(100) NULL,
        background_url VARCHAR(500) NOT NULL,
        is_active BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )
''')

# Insert default record
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
cursor.execute('''
    INSERT INTO services_servicesherosettings 
    (title, subtitle, background_url, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    'Our Services',
    'Comprehensive Real Estate Solutions',
    'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
    1,
    now,
    now
))

conn.commit()
print('SUCCESS: Table created')
conn.close()
"
