from rest_framework import serializers
from .models import ChatSession, ChatMessage
import re
import html


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for individual chat messages with security validation
    """
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'response', 'intent', 'confidence', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for chat sessions with message history
    """
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming chat requests with security validation
    
    Security Features:
    - Message length validation (max 500 chars)
    - XSS prevention (strip HTML tags and scripts)
    - SQL injection pattern detection
    - Input trimming and normalization
    """
    message = serializers.CharField(
        required=True,
        max_length=500,
        error_messages={
            'required': 'Message is required',
            'max_length': 'Message is too long (max 500 characters)',
            'blank': 'Message cannot be empty'
        }
    )
    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100
    )
    
    def validate_message(self, value):
        """
        Validate and sanitize message input
        
        Security checks:
        1. Remove HTML tags and scripts
        2. Detect SQL injection patterns
        3. Trim and normalize whitespace
        4. Check for dangerous patterns
        """
        if not value or not value.strip():
            raise serializers.ValidationError('Message cannot be empty')
        
        # Trim whitespace
        value = value.strip()
        
        # Remove HTML tags and scripts (XSS prevention)
        # First remove script tags completely
        value = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', value, flags=re.IGNORECASE)
        # Remove complete HTML tags (must have both < and > with tag name immediately after <)
        # This pattern requires a word character immediately after < (no space) to be considered a tag
        value = re.sub(r'<\w+[^>]*>', '', value)  # Opening tags like <div>, <span class="x">
        value = re.sub(r'</\w+>', '', value)  # Closing tags like </div>, </span>
        
        # Check for SQL injection patterns BEFORE escaping HTML entities
        # (to avoid false positives from HTML entity semicolons like &lt;)
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\bOR\b.*=.*)",
            r"(\bAND\b.*=.*)",
            r"('|\")\s*(OR|AND)\s*('|\")",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError('Invalid characters detected in message')
        
        # Escape remaining HTML entities (like standalone < or >) AFTER SQL checks
        value = html.escape(value, quote=False)
        
        # Check for dangerous JavaScript patterns
        js_patterns = [
            r'javascript:',
            r'on\w+\s*=',
            r'eval\(',
            r'expression\(',
        ]
        
        for pattern in js_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError('Invalid characters detected in message')
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        # Final length check after sanitization
        if len(value) > 500:
            raise serializers.ValidationError('Message is too long after sanitization')
        
        return value
    
    def validate_session_id(self, value):
        """Validate session ID format"""
        if value:
            # Only allow alphanumeric and hyphens
            if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
                raise serializers.ValidationError('Invalid session ID format')
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    response = serializers.CharField()
    session_id = serializers.CharField()
    intent = serializers.CharField(required=False, allow_blank=True)
    confidence = serializers.FloatField(required=False)


class MessageHistorySerializer(serializers.Serializer):
    """
    Serializer for message history in frontend format
    
    Returns messages in the format expected by the frontend:
    {
        "id": "uuid",
        "role": "user" | "bot",
        "message": "text",
        "timestamp": "ISO 8601"
    }
    """
    id = serializers.UUIDField()
    role = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()
