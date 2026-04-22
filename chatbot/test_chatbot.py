"""
Simple test script for the chatbot
Run with: python manage.py shell < chatbot/test_chatbot.py
"""

from chatbot.chatbot_engine import ChatbotEngine

def test_chatbot():
    print("=" * 60)
    print("CHATBOT TEST")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    test_messages = [
        "Hello!",
        "I'm looking for a 3 bedroom house",
        "What's the price range?",
        "Can I schedule a viewing?",
        "How do I contact an agent?",
        "I want to sell my property",
        "Tell me about mortgages",
        "Thanks, goodbye!"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        result = chatbot.process_message(message)
        print(f"Bot: {result['response']}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print("-" * 60)

if __name__ == "__main__":
    test_chatbot()
