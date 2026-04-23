# Convert category field from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_migrate_category_data'),
    ]

    operations = [
        # Step 0: Remove the existing index on category field
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS blog_blogpo_categor_481d67_idx",
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 1: Rename the old category field to category_old
        migrations.RenameField(
            model_name='blogpost',
            old_name='category',
            new_name='category_old',
        ),
        
        # Step 2: Add the new category field as a ForeignKey (nullable for now)
        migrations.AddField(
            model_name='blogpost',
            name='category',
            field=models.ForeignKey(
                blank=True,
                help_text='Blog category',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='blog.blogcategory'
            ),
        ),
        
        # Step 3: Populate the new category field with proper foreign key references
        migrations.RunSQL(
            sql="""
                UPDATE blog_blogpost 
                SET category_id = (
                    SELECT id FROM blog_blogcategory 
                    WHERE blog_blogcategory.name = blog_blogpost.category_old
                )
                WHERE category_old IS NOT NULL AND category_old != ''
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 4: Remove the old category_old field
        migrations.RemoveField(
            model_name='blogpost',
            name='category_old',
        ),
        
        # Step 5: Update the content field to use RichTextUploadingField
        migrations.AlterField(
            model_name='blogpost',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(
                help_text='Full blog post content with rich text editor'
            ),
        ),
        
        # Step 6: Handle tags field - rename old tags, add new ManyToMany
        migrations.RenameField(
            model_name='blogpost',
            old_name='tags',
            new_name='tags_old',
        ),
        
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.ManyToManyField(
                blank=True,
                help_text='Blog tags',
                related_name='posts',
                to='blog.blogtag'
            ),
        ),
        
        # Step 7: Remove old tags field
        migrations.RemoveField(
            model_name='blogpost',
            name='tags_old',
        ),
        
        # Step 8: Update indexes
        migrations.AlterModelOptions(
            name='blogpost',
            options={
                'ordering': ['-published_at'],
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
            },
        ),
        
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['-published_at'], name='blog_blogpo_publish_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['slug'], name='blog_blogpo_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['category'], name='blog_blogpo_categor_idx'),
        ),
    ]
