from django.db import models
from django.core.exceptions import ValidationError


class HeroSettings(models.Model):
    """Singleton model for hero section settings"""
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    background_image = models.ImageField(upload_to='home/hero/', blank=True, null=True)
    primary_button_text = models.CharField(max_length=50, default='View Properties')
    primary_button_link = models.CharField(max_length=200, default='/properties')
    secondary_button_text = models.CharField(max_length=50, default='Contact Me')
    secondary_button_link = models.CharField(max_length=200, default='/contact')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Settings'
        verbose_name_plural = 'Hero Settings'

    def save(self, *args, **kwargs):
        if not self.pk and HeroSettings.objects.exists():
            raise ValidationError('Only one Hero Settings instance is allowed.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Hero Settings cannot be deleted.')

    def __str__(self):
        return 'Hero Settings'


class HeroCard(models.Model):
    """Cards displayed below the hero section"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text='Icon name (e.g., home, key, building, dollar-sign)')
    link = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Hero Card'
        verbose_name_plural = 'Hero Cards'

    def __str__(self):
        return self.title


class HowItWorksStep(models.Model):
    """Steps in the How It Works section"""
    number = models.IntegerField(unique=True, help_text='Step number (1, 2, 3)')
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text='Icon name (e.g., search, file-text, key)')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'number']
        verbose_name = 'How It Works Step'
        verbose_name_plural = 'How It Works Steps'

    def __str__(self):
        return f'Step {self.number}: {self.title}'


class Neighborhood(models.Model):
    """Popular neighborhoods section"""
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='home/neighborhoods/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Neighborhood'
        verbose_name_plural = 'Neighborhoods'

    def __str__(self):
        return self.name


class Benefit(models.Model):
    """Benefits list items"""
    benefits_section = models.ForeignKey(
        'BenefitsSection',
        on_delete=models.CASCADE,
        related_name='benefits',
        null=True,
        blank=True
    )
    text = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Benefit Item'
        verbose_name_plural = 'Benefit Items'

    def __str__(self):
        return self.text[:50]


class BenefitGalleryImage(models.Model):
    """Gallery images in benefits section"""
    benefits_section = models.ForeignKey(
        'BenefitsSection',
        on_delete=models.CASCADE,
        related_name='gallery_images',
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='home/benefits/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return f'Gallery Image {self.id}'


class BenefitsSection(models.Model):
    """Singleton model for benefits section - manages all benefits components"""
    title = models.CharField(max_length=200, default='Why Choose Us')
    description = models.TextField(default='My objective is to not only have a good impact on ourselves and our families but also to inspire, encourage, and affect long-term change in everyone we meet.')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Benefits Section'
        verbose_name_plural = 'Benefits Section'

    def save(self, *args, **kwargs):
        if not self.pk and BenefitsSection.objects.exists():
            raise ValidationError('Only one Benefits Section instance is allowed.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Benefits Section cannot be deleted.')

    def __str__(self):
        return 'Benefits Section'


class ContactSectionSettings(models.Model):
    """Singleton model for contact section settings"""
    person_image = models.ImageField(upload_to='home/contact/')
    card_title = models.CharField(max_length=200)
    card_subtitle = models.CharField(max_length=200)
    card_description = models.TextField()
    button_text = models.CharField(max_length=50, default='Contact Me')
    button_link = models.CharField(max_length=200, default='/contact')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Section Settings'
        verbose_name_plural = 'Contact Section Settings'

    def save(self, *args, **kwargs):
        if not self.pk and ContactSectionSettings.objects.exists():
            raise ValidationError('Only one Contact Section Settings instance is allowed.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Contact Section Settings cannot be deleted.')

    def __str__(self):
        return 'Contact Section Settings'


class InstagramImage(models.Model):
    """Instagram feed images"""
    image = models.ImageField(upload_to='home/instagram/')
    link = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Instagram Image'
        verbose_name_plural = 'Instagram Images'

    def __str__(self):
        return f'Instagram Image {self.id}'


class PersonSectionSettings(models.Model):
    """Singleton model for person section settings"""
    title = models.TextField()
    description = models.TextField()
    person_image = models.ImageField(upload_to='home/person/')
    button_text = models.CharField(max_length=50, default='Contact Me')
    button_link = models.CharField(max_length=200, default='/contact')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Person Section Settings'
        verbose_name_plural = 'Person Section Settings'

    def save(self, *args, **kwargs):
        if not self.pk and PersonSectionSettings.objects.exists():
            raise ValidationError('Only one Person Section Settings instance is allowed.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Person Section Settings cannot be deleted.')

    def __str__(self):
        return 'Person Section Settings'


class StatItem(models.Model):
    """Stats section items"""
    icon_name = models.CharField(max_length=50, help_text='Icon name (e.g., crown, users, map-pinned, star)')
    label = models.CharField(max_length=100)
    description = models.TextField(help_text='Text shown on hover')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Stat Item'
        verbose_name_plural = 'Stat Items'

    def __str__(self):
        return self.label
