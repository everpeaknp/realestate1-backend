from __future__ import annotations

from django.core.management.base import BaseCommand

from properties.reaxml_importer import import_reaxml_feed


class Command(BaseCommand):
    help = 'Import Eagle REAXML feed listings from FTP or local XML files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-ftp',
            action='store_true',
            help='Download XML feed files from FTP credentials configured in environment variables.',
        )
        parser.add_argument(
            '--local-dir',
            type=str,
            default='',
            help='Import all *.xml files from a local directory.',
        )
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='Mark listings not present in this import set as inactive.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and calculate changes without writing to the database.',
        )

    def handle(self, *args, **options):
        summary = import_reaxml_feed(
            from_ftp=bool(options['from_ftp']),
            local_dir=options['local_dir'] or None,
            deactivate_missing=bool(options['deactivate_missing']),
            dry_run=bool(options['dry_run']),
        )

        self.stdout.write(self.style.SUCCESS('REAXML import finished'))
        self.stdout.write(f"Source: {summary['source'] or 'not set'}")
        self.stdout.write(f"Files processed: {summary['files_processed']}")
        self.stdout.write(f"Records parsed: {summary['records_parsed']}")
        self.stdout.write(f"Created: {summary['created']}")
        self.stdout.write(f"Updated: {summary['updated']}")
        self.stdout.write(f"Dry run: {summary['dry_run']}")
