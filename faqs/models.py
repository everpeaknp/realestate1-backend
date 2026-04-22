from django.db import models


class FAQ(models.Model):
    """FAQ model for frequently asked questions"""
    
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, default="General")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.question
