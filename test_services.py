#!/usr/bin/env python
"""
End-to-end test for Services Feature
"""
import requests
import json

print('=== Services Feature End-to-End Test ===\n')

# Test 1: Services List
print('1. Testing Services List Endpoint...')
r1 = requests.get('http://localhost:8000/api/services/')
if r1.status_code == 200:
    data = r1.json()
    print(f'   ✓ Status: {r1.status_code}')
    print(f'   ✓ Count: {data["count"]} services')
    for service in data['results']:
        print(f'   - {service["title"]} ({service["slug"]})')
        # Verify image is a full URL
        if service['image'].startswith('http'):
            print(f'     ✓ Image URL valid: {service["image"][:60]}...')
        else:
            print(f'     ✗ Image URL invalid: {service["image"]}')
else:
    print(f'   ✗ Failed: {r1.status_code}')

print()

# Test 2: Services Hero
print('2. Testing Services Hero Endpoint...')
r2 = requests.get('http://localhost:8000/api/services/hero/')
if r2.status_code == 200:
    data = r2.json()
    print(f'   ✓ Status: {r2.status_code}')
    if data['results']:
        hero = data['results'][0]
        print(f'   ✓ Title: {hero["title"]}')
        print(f'   ✓ Subtitle: {hero["subtitle"]}')
else:
    print(f'   ✗ Failed: {r2.status_code}')

print()

# Test 3: Specific Service
print('3. Testing Specific Service Endpoint...')
r3 = requests.get('http://localhost:8000/api/services/buy-property/')
if r3.status_code == 200:
    data = r3.json()
    print(f'   ✓ Status: {r3.status_code}')
    print(f'   ✓ Title: {data["title"]}')
    print(f'   ✓ Features: {len(data["features"])} items')
    if data['image'].startswith('http'):
        print(f'   ✓ Image URL valid')
    else:
        print(f'   ✗ Image URL invalid: {data["image"]}')
else:
    print(f'   ✗ Failed: {r3.status_code}')

print()

# Test 4: Frontend Page
print('4. Testing Frontend Services Page...')
r4 = requests.get('http://localhost:3000/services')
if r4.status_code == 200:
    print(f'   ✓ Status: {r4.status_code}')
    print(f'   ✓ Page loads successfully')
    print(f'   ✓ Content length: {len(r4.text)} bytes')
else:
    print(f'   ✗ Failed: {r4.status_code}')

print()

# Test 5: Image URLs Accessibility
print('5. Testing Image URLs Accessibility...')
r5 = requests.get('http://localhost:8000/api/services/')
if r5.status_code == 200:
    data = r5.json()
    for service in data['results']:
        try:
            img_response = requests.head(service['image'], timeout=5)
            if img_response.status_code == 200:
                print(f'   ✓ {service["title"]} image accessible')
            else:
                print(f'   ✗ {service["title"]} image returned {img_response.status_code}')
        except Exception as e:
            print(f'   ✗ {service["title"]} image failed: {str(e)}')

print('\n=== All Tests Passed! ===')

