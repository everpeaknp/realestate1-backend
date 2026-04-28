"""
Management command to import all images from backend/media/blog/gallery/ into GalleryImage model
"""
import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from gallery.models import GalleryImage


class Command(BaseCommand):
    help = 'Import all images from media/blog/gallery/ directory into GalleryImage model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing gallery images before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = GalleryImage.objects.count()
            GalleryImage.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Cleared {count} existing gallery images')
            )

        # Get the media directory path
        media_root = default_storage.location
        gallery_path = os.path.join(media_root, 'blog', 'gallery')

        if not os.path.exists(gallery_path):
            self.stdout.write(
                self.style.ERROR(f'Gallery path does not exist: {gallery_path}')
            )
            return

        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        imported_count = 0
        skipped_count = 0

        for filename in sorted(os.listdir(gallery_path)):
            file_path = os.path.join(gallery_path, filename)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Check if file has image extension
            _, ext = os.path.splitext(filename)
            if ext.lower() not in image_extensions:
                continue

            # Check if image already exists in database
            relative_path = f'blog/gallery/{filename}'
            if GalleryImage.objects.filter(image=relative_path).exists():
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Skipped (already exists): {filename}')
                )
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
                    self.style.SUCCESS(f'Imported: {filename}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing {filename}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Import complete!\n'
                f'  Imported: {imported_count}\n'
                f'  Skipped: {skipped_count}'
            )
        )
