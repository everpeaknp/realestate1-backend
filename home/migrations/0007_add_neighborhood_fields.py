# Generated manually for adding description and price_range to Neighborhood

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_benefitssection_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighborhood',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the neighborhood'),
        ),
        migrations.AddField(
            model_name='neighborhood',
            name='price_range',
            field=models.CharField(blank=True, help_text='e.g., $800k — $1.5M', max_length=100),
        ),
    ]
