#!/bin/bash
cd /opt/stacks/realestate1
docker compose run --rm realestate1-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db.sqlite3')
conn.execute('DROP TABLE IF EXISTS services_service_new')
conn.commit()
print('Cleaned up temporary table')
"
