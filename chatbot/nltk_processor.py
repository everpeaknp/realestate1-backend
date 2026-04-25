"""
NLTK-based Natural Language Processing for Chatbot
"""
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import re
import os


class NLTKProcessor:
    """Process natural language using NLTK"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.sia = None
        self._download_required_data()
        
    def _download_required_data(self):
        """Download required NLTK data"""
        required_data = [
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('sentiment/vader_lexicon', 'vader_lexicon'),
            ('corpora/omw-1.4', 'omw-1.4'),
        ]
        
        for path, package in required_data:
            try:
                nltk.data.find(path)
            except LookupError:
                try:
                    print(f"Downloading NLTK data: {package}...")
                    nltk.download(package, quiet=True)
                except Exception as e:
                    print(f"Warning: Could not download {package}: {e}")
        
        # Initialize sentiment analyzer
        try:
            self.sia = SentimentIntensityAnalyzer()
        except Exception as e:
            print(f"Warning: Could not initialize sentiment analyzer: {e}")
            self.sia = None
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        tokens = self.preprocess_text(text)
        return tokens
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        if self.sia:
            scores = self.sia.polarity_scores(text)
            return scores
        return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
    
    def detect_intent(self, text):
        """Detect user intent from text"""
        keywords = self.extract_keywords(text)
        text_lower = text.lower()
        
        # Real estate specific intents
        intents = {
            'property_search': ['property', 'house', 'home', 'apartment', 'condo', 'buy', 'purchase', 'looking', 'find', 'show', 'available', 'listing'],
            'property_details': ['detail', 'information', 'tell', 'about', 'describe', 'feature', 'amenity'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'budget', 'afford', 'payment', 'range'],
            'location': ['location', 'area', 'neighborhood', 'near', 'close', 'distance', 'where', 'city'],
            'schedule_viewing': ['visit', 'viewing', 'tour', 'schedule', 'appointment', 'see property', 'show property'],
            'contact': ['contact', 'call', 'email', 'reach', 'agent', 'speak', 'talk', 'phone'],
            'sell_property': ['sell', 'selling', 'list my', 'listing my', 'market my', 'want to sell', 'need to sell'],
            'rent': ['rent', 'rental', 'lease', 'tenant', 'renting'],
            'mortgage': ['mortgage', 'loan', 'financing', 'bank', 'interest', 'pre-approved'],
            'investment': ['investment', 'invest', 'portfolio', 'roi', 'return', 'yield', 'capital growth', 'passive income', 'wealth', 'investor'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'],
            'goodbye': ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'later'],
            'help': ['help', 'assist', 'support', 'question', 'faq'],
        }
        
        # Calculate intent scores
        intent_scores = {}
        for intent, intent_keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in intent_keywords)
            # Also check for exact phrases
            for keyword in intent_keywords:
                if keyword in text_lower:
                    score += 0.5
            intent_scores[intent] = score
        
        # Get the intent with highest score
        if intent_scores:
            max_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[max_intent]
            
            if max_score > 0:
                confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
                return max_intent, confidence
        
        return 'general', 0.5
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        tokens = word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        
        entities = {
            'numbers': [],
            'locations': [],
            'proper_nouns': []
        }
        
        # Extract numbers (potential prices, bedrooms, etc.)
        numbers = re.findall(r'\d+', text)
        entities['numbers'] = numbers
        
        # Extract proper nouns (potential locations, names)
        for word, pos in pos_tags:
            if pos == 'NNP':
                entities['proper_nouns'].append(word)
        
        return entities
