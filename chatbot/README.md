# Chatbot with NLTK Integration

This chatbot application uses NLTK (Natural Language Toolkit) for natural language processing to provide intelligent responses to user queries about real estate.

## Features

- **Intent Detection**: Automatically detects user intent from messages
- **Sentiment Analysis**: Analyzes the sentiment of user messages
- **Entity Extraction**: Extracts important entities like numbers, locations, and proper nouns
- **Context-Aware Responses**: Generates appropriate responses based on detected intent
- **Session Management**: Maintains conversation history across sessions
- **Real Estate Specific**: Tailored responses for property search, pricing, scheduling, etc.

## API Endpoints

### 1. Send Chat Message
```
POST /api/chatbot/chat/
```

**Request Body:**
```json
{
  "message": "Hello, I'm looking for a 3 bedroom house",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Hello! Welcome to Realtor Pal...",
  "session_id": "abc123...",
  "intent": "property_search",
  "confidence": 0.85
}
```

### 2. Get Chat History
```
GET /api/chatbot/history/?session_id=xxx
```

**Response:**
```json
{
  "id": 1,
  "session_id": "abc123...",
  "messages": [
    {
      "id": 1,
      "message": "Hello",
      "response": "Hi there!",
      "intent": "greeting",
      "confidence": 0.95,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### 3. Clear Session
```
DELETE /api/chatbot/clear_session/?session_id=xxx
```

### 4. Health Check
```
GET /api/chatbot/health/
```

## Supported Intents

The chatbot can detect and respond to the following intents:

1. **greeting** - Welcome messages
2. **goodbye** - Farewell messages
3. **property_search** - Looking for properties
4. **property_details** - Asking about specific property details
5. **pricing** - Questions about prices and budgets
6. **location** - Location-based queries
7. **schedule_viewing** - Scheduling property tours
8. **contact** - Contacting agents
9. **sell_property** - Selling property inquiries
10. **rent** - Rental property queries
11. **mortgage** - Mortgage and financing questions
12. **help** - General help requests

## NLTK Features Used

- **Tokenization**: Breaking text into words
- **Stopword Removal**: Filtering out common words
- **Lemmatization**: Converting words to base form
- **Sentiment Analysis**: Using VADER sentiment analyzer
- **POS Tagging**: Part-of-speech tagging for entity extraction

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

3. NLTK data will be downloaded automatically on first use

## Usage Example

```python
import requests

# Send a message
response = requests.post('http://localhost:8000/api/chatbot/chat/', json={
    'message': 'I want to buy a house with 3 bedrooms'
})

data = response.json()
print(f"Bot: {data['response']}")
print(f"Intent: {data['intent']}")
print(f"Session ID: {data['session_id']}")
```

## Admin Interface

The chatbot includes Django admin integration for:
- Viewing chat sessions
- Browsing message history
- Analyzing intent detection accuracy
- Monitoring chatbot performance

Access at: `http://localhost:8000/admin/chatbot/`

## Customization

### Adding New Intents

Edit `chatbot/nltk_processor.py` and add new intent keywords:

```python
intents = {
    'your_new_intent': ['keyword1', 'keyword2', 'keyword3'],
    # ...
}
```

Then add a handler in `chatbot/chatbot_engine.py`:

```python
def _handle_your_new_intent(self, message, entities, sentiment):
    return "Your custom response"
```

### Modifying Responses

Edit the response handlers in `chatbot/chatbot_engine.py` to customize bot responses.

## Testing

Test the chatbot with various queries:

```bash
# Test greeting
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test property search
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a 3 bedroom house under $500000"}'
```

## Performance

- First message may take 1-2 seconds as NLTK downloads required data
- Subsequent messages respond in < 100ms
- Session data is stored in database for persistence

## Future Enhancements

- Machine learning model training on conversation data
- Multi-language support
- Voice input/output integration
- Integration with property recommendation engine
- Advanced context tracking across multiple sessions
