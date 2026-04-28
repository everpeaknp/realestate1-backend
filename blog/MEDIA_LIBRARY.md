# Blog Media Library Management

## Overview

The BlogGalleryImage model provides a unified media library for managing all images across the application. Images must be registered in the database to appear in the admin interface at `/admin/blog/bloggalleryimage/`.

## Management Commands

### 1. Import All Media Files

Import all images from the `backend/media/` directory into the database:

```bash
python manage.py import_all_media
```

**Options:**
- `--clear`: Clear all existing gallery images before importing
- `--exclude-dirs`: Comma-separated list of directories to exclude (e.g., `"blog/featured,properties/main"`)

**Example:**
```bash
# Import all media files
python manage.py import_all_media

# Clear and re-import everything
python manage.py import_all_media --clear

# Import but exclude certain directories
python manage.py import_all_media --exclude-dirs="blog/featured,properties/main"
```

### 2. Import Gallery Images Only

Import only images from `backend/media/blog/gallery/`:

```bash
python manage.py import_gallery_images
```

**Options:**
- `--clear`: Clear all existing gallery images before importing

## Features

### WordPress-Style Media Library

The admin interface at `/admin/blog/bloggalleryimage/` provides:

- **Thumbnail Preview**: Visual preview of each image
- **File Information**: File name, size, and dimensions
- **Metadata**: Caption and alt text for accessibility
- **Attachment Status**: Shows which post (if any) the image is attached to
- **Filtering**: Filter by creation date or attachment status
- **Search**: Search by caption, alt text, or filename
- **Bulk Actions**: Detach images from posts in bulk

### Image Properties

Each image record includes:

- `image`: The image file path
- `caption`: Optional caption text
- `alt_text`: Alt text for accessibility (auto-populated with filename on import)
- `post`: Optional ForeignKey to BlogPost (null=True for unattached images)
- `order`: Display order
- `created_at`: Timestamp when added to database

## Workflow

### Adding New Images

1. **Upload via Admin**: Upload images directly through the admin interface
2. **Upload via Form**: Use the image upload form in blog post creation
3. **Import from Filesystem**: Use management commands to import existing files

### Organizing Images

1. **Attach to Posts**: Link images to blog posts via the inline gallery editor
2. **Unattached Images**: Keep images unattached for reuse across multiple posts
3. **Bulk Operations**: Use admin actions to detach multiple images at once

### Viewing All Media

Visit `/admin/blog/bloggalleryimage/` to see:
- All 211+ images from the media directory
- Organized by creation date
- Filterable by attachment status
- Searchable by filename, caption, or alt text

## Database Schema

```python
class BlogGalleryImage(models.Model):
    post = ForeignKey(BlogPost, null=True, blank=True)  # Optional attachment
    image = ImageField(upload_to='blog/gallery/')
    caption = CharField(max_length=200, blank=True)
    alt_text = CharField(max_length=200, blank=True)
    order = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
```

## Notes

- Images are stored in `backend/media/` with organized subdirectories
- Database records are required for admin visibility
- Unattached images (post=None) are useful for shared media libraries
- Alt text is auto-populated from filename on import but should be customized
- The admin supports pagination (50 items per page by default)
