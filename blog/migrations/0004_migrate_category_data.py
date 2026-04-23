# Data migration to populate BlogCategory from existing category strings

from django.db import migrations
from django.utils.text import slugify


def migrate_categories_forward(apps, schema_editor):
    """Create BlogCategory objects from existing category strings"""
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    
    # Use raw SQL to get unique category values from existing posts
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT category FROM blog_blogpost WHERE category != ''")
        categories = [row[0] for row in cursor.fetchall()]
    
    # Create BlogCategory objects for each unique category
    db_alias = schema_editor.connection.alias
    for category_name in categories:
        if category_name:
            slug = slugify(category_name)
            BlogCategory.objects.using(db_alias).get_or_create(
                name=category_name,
                defaults={'slug': slug, 'description': f'{category_name} articles'}
            )


def migrate_categories_backward(apps, schema_editor):
    """Remove created categories"""
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    BlogCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_create_category_tag_models'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_forward, migrate_categories_backward),
    ]
