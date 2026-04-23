#!/usr/bin/env python
"""
Simple script to test the Projects API endpoint
"""
import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_projects_api():
    """Test the projects API endpoint"""
    print("Testing Projects API...")
    print("-" * 50)
    
    try:
        # Test list endpoint
        response = requests.get(f"{API_URL}/api/projects/")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ API is accessible")
        print(f"✓ Total projects: {data['count']}")
        
        if data['results']:
            first_project = data['results'][0]
            print(f"✓ First project: {first_project['title']}")
            print(f"✓ Images in first project: {len(first_project['images'])}")
            
            if first_project['images']:
                first_image = first_project['images'][0]
                print(f"✓ First image URL: {first_image['image']}")
                
                # Test if image is accessible
                img_response = requests.head(first_image['image'])
                if img_response.status_code == 200:
                    print(f"✓ Image is accessible")
                else:
                    print(f"✗ Image not accessible (status: {img_response.status_code})")
        
        # Test featured endpoint
        featured_response = requests.get(f"{API_URL}/api/projects/featured/")
        featured_response.raise_for_status()
        featured_data = featured_response.json()
        print(f"✓ Featured projects: {len(featured_data)}")
        
        print("-" * 50)
        print("All tests passed! ✓")
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API. Is the Django server running?")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    test_projects_api()
