# Projects App

The Projects app manages the portfolio of completed real estate projects with image galleries.

## Features

- ✅ Project management with categories (Residential, Commercial, Luxury, etc.)
- ✅ Multiple images per project with ordering
- ✅ Featured projects support
- ✅ RESTful API with full CRUD operations (admin only)
- ✅ Image upload and management
- ✅ Responsive image URLs with full domain
- ✅ Admin interface with inline image management

## Models

### Project
- `title`: Project name
- `description`: Detailed project description
- `location`: Project location
- `completion_date`: When the project was completed
- `category`: Project category (RESIDENTIAL, COMMERCIAL, RENOVATION, LUXURY, MODERN, TRADITIONAL)
- `is_featured`: Whether to feature on homepage
- `order`: Display order (lower numbers first)

### ProjectImage
- `project`: Foreign key to Project
- `image`: Image file (uploaded to `media/projects/`)
- `title`: Image title
- `caption`: Optional image caption
- `order`: Display order within project

## API Endpoints

### List all projects
```
GET /api/projects/
```

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern Villa Exterior",
      "description": "A stunning modern villa...",
      "images": [
        {
          "id": 1,
          "image": "http://127.0.0.1:8000/media/projects/project_1_image_0.jpg",
          "title": "Modern Villa Exterior - View 1",
          "caption": "",
          "order": 0
        }
      ],
      "location": "Beverly Hills, CA",
      "completion_date": "2025-05-04",
      "category": "Luxury",
      "is_featured": true,
      "order": 1,
      "created_at": "2026-04-23T10:04:06.596297Z"
    }
  ]
}
```

### Get single project
```
GET /api/projects/{id}/
```

### Get featured projects
```
GET /api/projects/featured/
```

### Get project categories
```
GET /api/projects/categories/
```

Response:
```json
{
  "categories": ["RESIDENTIAL", "COMMERCIAL", "LUXURY", "MODERN"]
}
```

## Management Commands

### Populate sample data
```bash
python manage.py populate_projects
```

This command:
- Clears existing projects
- Creates 5 sample projects with different categories
- Downloads and saves real images from Unsplash
- Sets up featured projects

## Admin Interface

Access the admin at `/admin/projects/`

Features:
- Inline image management
- Image preview thumbnails
- Bulk actions (mark as featured, remove featured)
- Category badges with colors
- Image count display
- Drag-and-drop ordering

## Frontend Integration

The ProjectGallery component (`frontend/src/components/projects/ProjectGallery.tsx`) automatically:
- Fetches all projects from the API
- Flattens all images into a masonry gallery
- Provides lightbox functionality with navigation
- Shows image titles on hover
- Handles loading and error states

## Image Handling

Images are:
- Uploaded to `media/projects/`
- Served with full absolute URLs
- Optimized for web display
- Ordered within each project

## Testing

Run the API test:
```bash
python backend/test_api.py
```

This verifies:
- API connectivity
- Project data structure
- Image accessibility
- Featured projects endpoint

## Configuration

In `settings.py`:
```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Ensure CORS is configured for frontend:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000'
]
```

## Security

- Read-only API for public access
- Admin authentication required for modifications
- Image uploads validated by Django
- CORS configured for specific origins

## Performance

- Prefetch related images in queries
- Indexed fields: order, completion_date, is_featured, category
- Pagination enabled (12 items per page)
- Optimized queries with `prefetch_related('images')`
