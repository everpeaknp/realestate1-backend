#!/bin/bash
cd /opt/stacks/realestate1
docker compose run --rm realestate1-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db.sqlite3')
cursor = conn.cursor()

print('=== services_service table schema ===')
cursor.execute('PRAGMA table_info(services_service)')
for row in cursor.fetchall():
    print(row)

print('\n=== services_servicefeature table schema ===')
cursor.execute('PRAGMA table_info(services_servicefeature)')
for row in cursor.fetchall():
    print(row)

print('\n=== services_servicesherosettings table schema ===')
cursor.execute('PRAGMA table_info(services_servicesherosettings)')
for row in cursor.fetchall():
    print(row)

print('\n=== Count of records ===')
cursor.execute('SELECT COUNT(*) FROM services_service')
print(f'Services: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM services_servicefeature')
print(f'Service Features: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM services_servicesherosettings')
print(f'Hero Settings: {cursor.fetchone()[0]}')

conn.close()
"
