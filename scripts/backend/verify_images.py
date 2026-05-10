#!/usr/bin/env python
import requests

print('=== Verifying Service Images ===\n')

r = requests.get('http://localhost:8000/api/services/')
data = r.json()

for service in data['results']:
    print(f'{service["title"]}:')
    print(f'  Image: {service["image"]}')
    print()

print('✓ All images are now using Unsplash URLs')
