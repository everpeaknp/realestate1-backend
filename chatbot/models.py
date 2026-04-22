from django.db import models
from django.utils import timezone


class ChatSession(models.Model):
    """Store chat sessions for tracking conversations"""
    session_id = models.CharField(max_length=100, unique=True)
    # Optional user info collected at chat start
    user_name  = models.CharField(max_length=200, blank=True, default='')
    user_email = models.EmailField(blank=True, default='')
    user_phone = models.CharField(max_length=30, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        label = self.user_name or self.user_email or self.session_id
        return f"Session {label}"


class ChatMessage(models.Model):
    """Store individual chat messages"""
    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message    = models.TextField()
    response   = models.TextField()
    intent     = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session.session_id} - {self.created_at}"


class ChatbotRule(models.Model):
    """
    Rule-based chatbot responses.
    Evaluated FIRST — before Knowledge Base, FAQs, and intent handlers.
    """

    MATCH_TYPE_CHOICES = [
        ('exact',      'Exact match  — message equals pattern exactly'),
        ('contains',   'Contains     — message contains the pattern'),
        ('startswith', 'Starts with  — message starts with the pattern'),
        ('endswith',   'Ends with    — message ends with the pattern'),
        ('regex',      'Regex        — full Python regex pattern'),
    ]

    name       = models.CharField(max_length=200, help_text="Internal name for this rule.")
    pattern    = models.CharField(max_length=500, help_text="Pattern to match against the user message.")
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default='contains')
    response   = models.TextField(help_text="Response to send when this rule matches.")
    priority   = models.PositiveIntegerField(default=0, help_text="Higher = evaluated first.")
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Chatbot Rule'
        verbose_name_plural = 'Chatbot Rules'

    def __str__(self):
        return f"[{self.get_match_type_display().split()[0]}] {self.name}"

    def matches(self, message: str) -> bool:
        import re as _re
        text = message.lower().strip()
        pat  = self.pattern.lower().strip()
        try:
            if self.match_type == 'exact':      return text == pat
            if self.match_type == 'contains':   return pat in text
            if self.match_type == 'startswith': return text.startswith(pat)
            if self.match_type == 'endswith':   return text.endswith(pat)
            if self.match_type == 'regex':      return bool(_re.search(self.pattern, message, _re.IGNORECASE))
        except Exception:
            pass
        return False


class KnowledgeBase(models.Model):
    """Admin-managed knowledge base for training the chatbot."""

    CATEGORY_CHOICES = [
        ('general',   'General'),
        ('services',  'Services'),
        ('pricing',   'Pricing'),
        ('process',   'Process'),
        ('legal',     'Legal'),
        ('contact',   'Contact & Hours'),
        ('properties','Properties'),
        ('financing', 'Financing'),
        ('buying',    'Buying'),
        ('selling',   'Selling'),
        ('renting',   'Renting'),
        ('about',     'About Us'),
        ('policies',  'Policies'),
        ('other',     'Other'),
    ]

    question   = models.CharField(max_length=500, help_text="The question customers ask.")
    answer     = models.TextField(help_text="The full answer the chatbot will give.")
    keywords   = models.CharField(max_length=500, blank=True, help_text="Comma-separated trigger words.")
    category   = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    priority   = models.PositiveIntegerField(default=0, help_text="Higher = checked first.")
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'question']
        verbose_name = 'Knowledge Base Entry'
        verbose_name_plural = 'Knowledge Base'

    def __str__(self):
        return self.question

    @property
    def keyword_list(self):
        if self.keywords.strip():
            return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]
        stop = {
            'what','how','why','when','where','who','which','is','are','do','does',
            'can','will','the','a','an','i','my','your','to','of','in','for','on',
            'with','at','by','from',
        }
        import re
        words = re.findall(r'\b\w+\b', self.question.lower())
        return [w for w in words if w not in stop and len(w) > 2]
