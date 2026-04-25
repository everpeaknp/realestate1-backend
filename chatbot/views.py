from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    MessageHistorySerializer
)
from .chatbot_engine import ChatbotEngine


class ChatbotRateThrottle(AnonRateThrottle):
    """
    Custom rate throttle for chatbot API
    Limits: 30 requests per minute per IP
    """
    rate = '30/min'


class ChatbotViewSet(viewsets.ViewSet):
    """
    ViewSet for chatbot interactions with security features:
    - Rate limiting (30 req/min)
    - Input sanitization
    - Session management
    - Message persistence
    """
    
    throttle_classes = [ChatbotRateThrottle]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = ChatbotEngine()
    
    def _check_spam(self, session_id: str, message: str) -> bool:
        """
        Check for spam/duplicate messages
        Returns True if spam detected
        """
        cache_key = f'chatbot_last_msg_{session_id}'
        last_message = cache.get(cache_key)
        
        if last_message == message:
            # Same message sent twice in a row
            return True
        
        # Store current message for 10 seconds
        cache.set(cache_key, message, 10)
        return False
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Process a chat message and return response
        
        POST /api/chatbot/chat/
        {
            "message": "Hello, I'm looking for a 3 bedroom house",
            "session_id": "optional-session-id"
        }
        
        Security Features:
        - Input validation and sanitization
        - Rate limiting (30 req/min)
        - Spam detection
        - XSS prevention
        - SQL injection prevention
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message    = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        # Optional user info (sent on first message)
        user_name  = request.data.get('user_name', '').strip()[:200]
        user_email = request.data.get('user_email', '').strip()[:254]
        user_phone = request.data.get('user_phone', '').strip()[:30]

        # Create or get session
        if not session_id:
            session_id = get_random_string(32)

        try:
            session, created = ChatSession.objects.get_or_create(session_id=session_id)
        except Exception as e:
            return Response(
                {'error': 'Failed to create session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Check for spam
        if not created and self._check_spam(session_id, message):
            return Response(
                {'error': 'Please wait before sending the same message again'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Store user info if provided and not already set
        updated = False
        if user_name  and not session.user_name:  session.user_name  = user_name;  updated = True
        if user_email and not session.user_email: session.user_email = user_email; updated = True
        if user_phone and not session.user_phone: session.user_phone = user_phone; updated = True
        if updated:
            session.save()

            # Create a Lead with user info + extract preferences from message
            try:
                from leads.models import Lead
                name_parts = user_name.split(' ', 1) if user_name else ['Chat', 'User']

                # Extract preferences from the message
                budget = ''
                prop_type = ''
                msg_lower = message.lower()

                # Budget extraction
                import re
                budget_match = re.search(r'\$?([\d,]+)\s*(?:k|thousand|lakh|crore|million)?', msg_lower)
                if budget_match:
                    budget = f"~{budget_match.group(0).strip()}"

                # Property type extraction
                for pt in ['apartment', 'house', 'villa', 'condo', 'land', 'plot', 'flat', 'studio', 'bhk']:
                    if pt in msg_lower:
                        prop_type = pt.upper()
                        break

                Lead.objects.get_or_create(
                    email=user_email or f'{session_id}@chat.local',
                    defaults={
                        'first_name':            name_parts[0],
                        'last_name':             name_parts[1] if len(name_parts) > 1 else '',
                        'phone':                 user_phone,
                        'inquiry_type':          'GENERAL',
                        'source':                'CHATBOT',
                        'message':               f'Chat session started. First message: {message[:200]}',
                        'subject':               'Chat Inquiry',
                        'budget':                budget,
                        'property_type_interest': prop_type,
                    }
                )
            except Exception:
                # Don't fail the chat if lead creation fails
                pass
        
        # Process message with chatbot engine
        try:
            result = self.chatbot.process_message(message, session_id)
        except Exception as e:
            return Response(
                {'error': 'Failed to process message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Save message and response
        try:
            chat_message = ChatMessage.objects.create(
                session=session,
                message=message,
                response=result['response'],
                intent=result.get('intent'),
                confidence=result.get('confidence')
            )
        except Exception:
            # Return response even if save fails
            pass
        
        # Prepare response
        response_data = {
            'response': result['response'],
            'session_id': session_id,
            'intent': result.get('intent'),
            'confidence': result.get('confidence')
        }
        
        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get chat history for a session in frontend-compatible format
        
        GET /api/chatbot/history/?session_id=xxx
        
        Returns:
        {
            "session_id": "xxx",
            "messages": [
                {
                    "id": "uuid",
                    "role": "user",
                    "message": "Hello",
                    "timestamp": "2025-01-24T10:00:00Z"
                },
                {
                    "id": "uuid",
                    "role": "bot",
                    "message": "Hi! How can I help?",
                    "timestamp": "2025-01-24T10:00:01Z"
                }
            ]
        }
        """
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = ChatSession.objects.get(session_id=session_id)
            chat_messages = session.messages.all()
            
            # Convert to frontend format
            messages = []
            for msg in chat_messages:
                # User message
                messages.append({
                    'id': str(uuid.uuid4()),
                    'role': 'user',
                    'message': msg.message,
                    'timestamp': msg.created_at.isoformat()
                })
                # Bot response
                messages.append({
                    'id': str(uuid.uuid4()),
                    'role': 'bot',
                    'message': msg.response,
                    'timestamp': msg.created_at.isoformat()
                })
            
            return Response({
                'session_id': session_id,
                'messages': messages
            }, status=status.HTTP_200_OK)
            
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def clear_session(self, request):
        """
        Clear a chat session
        
        DELETE /api/chatbot/clear_session/?session_id=xxx
        """
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = ChatSession.objects.get(session_id=session_id)
            session.delete()
            
            # Clear cache
            cache_key = f'chatbot_last_msg_{session_id}'
            cache.delete(cache_key)
            
            return Response(
                {'message': 'Session cleared successfully'},
                status=status.HTTP_200_OK
            )
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Health check endpoint
        
        GET /api/chatbot/health/
        """
        return Response({
            'status': 'healthy',
            'service': 'chatbot',
            'nltk_available': True,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
