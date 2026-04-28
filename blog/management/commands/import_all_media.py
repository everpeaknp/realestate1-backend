"""
Management command to import ALL images from backend/media/ into GalleryImage model
This creates a unified media library accessible from the admin
"""
import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from gallery.models import GalleryImage


class Command(BaseCommand):
    help = 'Import all images from media/ directory into GalleryImage model (unified media library)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing gallery images before importing',
        )
        parser.add_argument(
            '--exclude-dirs',
            type=str,
            default='',
            help='Comma-separated list of directories to exclude (e.g., "blog/featured,properties/main")',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = GalleryImage.objects.count()
            GalleryImage.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Cleared {count} existing gallery images')
            )

        # Parse exclude directories
        exclude_dirs = set()
        if options['exclude_dirs']:
            exclude_dirs = set(d.strip() for d in options['exclude_dirs'].split(','))

        # Get the media directory path
        media_root = default_storage.location

        if not os.path.exists(media_root):
            self.stdout.write(
                self.style.ERROR(f'Media path does not exist: {media_root}')
            )
            return

        # Image extensions to look for
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        imported_count = 0
        skipped_count = 0
        error_count = 0

        # Walk through all directories in media
        for root, dirs, files in os.walk(media_root):
            for filename in sorted(files):
                file_path = os.path.join(root, filename)

                # Check if file has image extension
                _, ext = os.path.splitext(filename)
                if ext.lower() not in image_extensions:
                    continue

                # Get relative path from media root
                relative_path = os.path.relpath(file_path, media_root)
                relative_path = relative_path.replace('\\', '/')  # Normalize path separators

                # Check if directory should be excluded
                should_exclude = False
                for exclude_dir in exclude_dirs:
                    if relative_path.startswith(exclude_dir):
                        should_exclude = True
                        break

                if should_exclude:
                    skipped_count += 1
                    continue

                # Check if image already exists in database
                if GalleryImage.objects.filter(image=relative_path).exists():
                    skipped_count += 1
                    continue

                # Create GalleryImage record
                try:
                    gallery_image = GalleryImage(
                        image=relative_path,
                        caption='',
                        alt_text=filename,
                        order=imported_count,
                    )
                    gallery_image.save()
                    imported_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Imported: {relative_path}')
                    )
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error importing {relative_path}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Import complete!\n'
                f'  Imported: {imported_count}\n'
                f'  Skipped: {skipped_count}\n'
                f'  Errors: {error_count}'
            )
        )
