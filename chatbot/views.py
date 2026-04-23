from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)
from .chatbot_engine import ChatbotEngine


class ChatbotViewSet(viewsets.ViewSet):
    """
    ViewSet for chatbot interactions
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = ChatbotEngine()
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Process a chat message and return response
        
        POST /api/chatbot/chat/
        {
            "message": "Hello, I'm looking for a 3 bedroom house",
            "session_id": "optional-session-id"
        }
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message    = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        # Optional user info (sent on first message)
        user_name  = request.data.get('user_name', '').strip()
        user_email = request.data.get('user_email', '').strip()
        user_phone = request.data.get('user_phone', '').strip()

        # Create or get session
        if not session_id:
            session_id = get_random_string(32)

        session, created = ChatSession.objects.get_or_create(session_id=session_id)

        # Store user info if provided and not already set
        updated = False
        if user_name  and not session.user_name:  session.user_name  = user_name;  updated = True
        if user_email and not session.user_email: session.user_email = user_email; updated = True
        if user_phone and not session.user_phone: session.user_phone = user_phone; updated = True
        if updated:
            session.save()

            # Create a Lead with user info + extract preferences from message
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
            for pt in ['apartment', 'house', 'villa', 'condo', 'land', 'plot', 'flat', 'studio', 'bhk', 'bhk']:
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
                    'message':               f'Chat session started. First message: {message}',
                    'subject':               'Chat Inquiry',
                    'budget':                budget,
                    'property_type_interest': prop_type,
                }
            )
        
        # Process message with chatbot engine
        result = self.chatbot.process_message(message, session_id)
        
        # Save message and response
        chat_message = ChatMessage.objects.create(
            session=session,
            message=message,
            response=result['response'],
            intent=result.get('intent'),
            confidence=result.get('confidence')
        )
        
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
        Get chat history for a session
        
        GET /api/chatbot/history/?session_id=xxx
        """
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = ChatSession.objects.get(session_id=session_id)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
            'nltk_available': True
        }, status=status.HTTP_200_OK)
