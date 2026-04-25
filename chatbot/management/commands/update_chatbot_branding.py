"""
Management command to update all Realtor Pal references to Lily White Real Estate in chatbot data
"""
from django.core.management.base import BaseCommand
from chatbot.models import ChatbotRule, KnowledgeBase, ChatSession, ChatMessage


class Command(BaseCommand):
    help = 'Update all Realtor Pal references to Lily White Real Estate in chatbot database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting chatbot branding update...'))
        
        # Update ChatbotRule
        rules_updated = 0
        for rule in ChatbotRule.objects.all():
            original_response = rule.response
            updated_response = original_response.replace('Realtor Pal', 'Lily White Real Estate')
            updated_response = updated_response.replace('realtorpal', 'lilywhiterealestate')
            
            if updated_response != original_response:
                rule.response = updated_response
                rule.save()
                rules_updated += 1
                self.stdout.write(f'  Updated rule: {rule.name}')
        
        # Update KnowledgeBase
        kb_updated = 0
        for entry in KnowledgeBase.objects.all():
            original_answer = entry.answer
            updated_answer = original_answer.replace('Realtor Pal', 'Lily White Real Estate')
            updated_answer = updated_answer.replace('realtorpal', 'lilywhiterealestate')
            
            if updated_answer != original_answer:
                entry.answer = updated_answer
                entry.save()
                kb_updated += 1
                self.stdout.write(f'  Updated KB: {entry.question}')
        
        # Update ChatMessage responses (historical data)
        messages_updated = 0
        for message in ChatMessage.objects.all():
            original_response = message.response
            updated_response = original_response.replace('Realtor Pal', 'Lily White Real Estate')
            updated_response = updated_response.replace('realtorpal', 'lilywhiterealestate')
            
            if updated_response != original_response:
                message.response = updated_response
                message.save()
                messages_updated += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Update Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'✓ ChatbotRules updated: {rules_updated}'))
        self.stdout.write(self.style.SUCCESS(f'✓ KnowledgeBase entries updated: {kb_updated}'))
        self.stdout.write(self.style.SUCCESS(f'✓ ChatMessages updated: {messages_updated}'))
        self.stdout.write(self.style.SUCCESS('\nAll chatbot data now uses "Lily White Real Estate"'))
