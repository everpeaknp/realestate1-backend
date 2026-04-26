"""
Modern Local NLP Processor
Uses spaCy for NER + sentence-transformers for semantic search.
100% local — no external API calls.

Install dependencies:
    pip install spacy sentence-transformers
    python -m spacy download en_core_web_sm
"""

import re
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Lazy imports — only load heavy models when first needed             #
# ------------------------------------------------------------------ #

_spacy_nlp = None
_sentence_model = None


def _get_spacy():
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy en_core_web_sm loaded")
        except Exception as e:
            logger.warning(f"spaCy unavailable ({e}), falling back to regex NER")
            _spacy_nlp = False  # Mark as unavailable
    return _spacy_nlp if _spacy_nlp else None


def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # all-MiniLM-L6-v2 is tiny (80MB), fast, and accurate enough
            _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer all-MiniLM-L6-v2 loaded")
        except Exception as e:
            logger.warning(f"sentence-transformers unavailable ({e}), falling back to keyword matching")
            _sentence_model = False
    return _sentence_model if _sentence_model else None


# ------------------------------------------------------------------ #
#  NER — Entity Extraction                                             #
# ------------------------------------------------------------------ #

class EntityExtractor:
    """
    Extracts structured entities from natural language using spaCy NER.
    Falls back to regex patterns if spaCy is unavailable.
    """

    # Regex fallbacks
    _BUDGET_PATTERNS = [
        (r'\$\s*([\d,]+)\s*k\b',          1_000),
        (r'\$\s*([\d,]+)\s*m(?:illion)?\b', 1_000_000),
        (r'\$\s*([\d,]+)',                  1),
        (r'([\d,]+)\s*k\b',               1_000),
        (r'([\d,]+)\s*(?:dollars?|usd)\b', 1),
        (r'under\s+([\d,]+)',              1),
        (r'below\s+([\d,]+)',              1),
        (r'max(?:imum)?\s+([\d,]+)',       1),
    ]

    _BED_PATTERN = re.compile(
        r'(\d+)\s*(?:bed(?:room)?s?|br\b)', re.IGNORECASE
    )

    _BATH_PATTERN = re.compile(
        r'(\d+)\s*(?:bath(?:room)?s?|ba\b)', re.IGNORECASE
    )

    _SQFT_PATTERN = re.compile(
        r'(\d[\d,]*)\s*(?:sq\.?\s*ft\.?|square\s*feet)', re.IGNORECASE
    )

    _PROP_TYPES = {
        'apartment': ['apartment', 'apt', 'flat', 'unit'],
        'house':     ['house', 'home', 'detached', 'bungalow'],
        'condo':     ['condo', 'condominium', 'townhouse', 'townhome'],
        'villa':     ['villa', 'mansion', 'estate'],
        'land':      ['land', 'lot', 'plot', 'acreage'],
        'studio':    ['studio'],
        'commercial':['commercial', 'office', 'retail', 'warehouse'],
    }

    def extract(self, text: str) -> dict:
        """
        Returns a dict with:
          budget_max, budget_min, beds, baths, sqft,
          locations, property_type, raw_entities
        """
        result = {
            'budget_max':    None,
            'budget_min':    None,
            'beds':          None,
            'baths':         None,
            'sqft':          None,
            'locations':     [],
            'property_type': None,
            'raw_entities':  [],
        }

        # --- spaCy NER ---
        nlp = _get_spacy()
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                result['raw_entities'].append({'text': ent.text, 'label': ent.label_})
                if ent.label_ in ('GPE', 'LOC', 'FAC'):
                    result['locations'].append(ent.text)
                elif ent.label_ == 'MONEY':
                    val = self._parse_money(ent.text)
                    if val:
                        if 'above' in text.lower() or 'over' in text.lower() or 'minimum' in text.lower():
                            result['budget_min'] = val
                        else:
                            result['budget_max'] = val
                elif ent.label_ == 'CARDINAL':
                    # Could be beds/baths/sqft — let regex handle specifics
                    pass

        # --- Regex fallbacks / supplements ---
        if result['budget_max'] is None:
            result['budget_max'] = self._extract_budget(text)

        bed_m = self._BED_PATTERN.search(text)
        if bed_m:
            result['beds'] = int(bed_m.group(1))

        bath_m = self._BATH_PATTERN.search(text)
        if bath_m:
            result['baths'] = int(bath_m.group(1))

        sqft_m = self._SQFT_PATTERN.search(text)
        if sqft_m:
            result['sqft'] = int(sqft_m.group(1).replace(',', ''))

        # Property type
        text_lower = text.lower()
        for ptype, keywords in self._PROP_TYPES.items():
            if any(kw in text_lower for kw in keywords):
                result['property_type'] = ptype
                break

        # City fallback from DB if spaCy found nothing
        if not result['locations']:
            result['locations'] = self._extract_cities_from_db(text)

        return result

    def _extract_budget(self, text: str) -> Optional[int]:
        for pattern, multiplier in self._BUDGET_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                try:
                    val = int(m.group(1).replace(',', '')) * multiplier
                    if val > 1000:  # Ignore tiny numbers
                        return val
                except (ValueError, IndexError):
                    pass
        return None

    def _parse_money(self, text: str) -> Optional[int]:
        """Parse spaCy MONEY entity text to integer."""
        text = text.replace(',', '').replace('$', '').strip()
        m = re.search(r'([\d.]+)\s*(k|m|million|thousand)?', text, re.IGNORECASE)
        if not m:
            return None
        try:
            val = float(m.group(1))
            suffix = (m.group(2) or '').lower()
            if suffix in ('k', 'thousand'):
                val *= 1_000
            elif suffix in ('m', 'million'):
                val *= 1_000_000
            return int(val)
        except ValueError:
            return None

    def _extract_cities_from_db(self, text: str) -> list:
        """Fallback: check if any known city name appears in the message."""
        try:
            from properties.models import Property
            cities = list(
                Property.objects.values_list('city', flat=True).distinct()
            )
            text_lower = text.lower()
            return [c for c in cities if c.lower() in text_lower]
        except Exception:
            return []


# ------------------------------------------------------------------ #
#  Semantic Search — Knowledge Base & FAQ                              #
# ------------------------------------------------------------------ #

class SemanticSearcher:
    """
    Builds in-memory vector index from Knowledge Base / FAQ entries.
    Uses cosine similarity to find the best matching answer.
    Falls back to keyword overlap if sentence-transformers unavailable.
    """

    def __init__(self):
        self._kb_index   = None   # (embeddings, entries)
        self._faq_index  = None
        self._kb_version = -1     # Track DB changes
        self._faq_version = -1

    # ---- Public API ----

    def search_knowledge_base(self, query: str, threshold: float = 0.45) -> Optional[str]:
        """Return best KB answer or None if below threshold."""
        model = _get_sentence_model()
        if not model:
            return self._keyword_search_kb(query)

        index = self._get_kb_index(model)
        if index is None:
            return None

        embeddings, entries = index
        return self._cosine_search(model, query, embeddings, entries, threshold)

    def search_faq(self, query: str, threshold: float = 0.40) -> Optional[str]:
        """Return best FAQ answer or None if below threshold."""
        model = _get_sentence_model()
        if not model:
            return self._keyword_search_faq(query)

        index = self._get_faq_index(model)
        if index is None:
            return None

        embeddings, entries = index
        result = self._cosine_search(model, query, embeddings, entries, threshold)
        if result:
            # Wrap in FAQ format
            entry = entries[self._last_match_idx]
            return (
                f"FAQ: {entry['question']}\n\n"
                f"{entry['answer']}\n\n"
                "Do you have another question? I'm happy to help."
            )
        return None

    # ---- Index builders ----

    def _get_kb_index(self, model):
        try:
            from .models import KnowledgeBase
            count = KnowledgeBase.objects.filter(is_active=True).count()
            if count != self._kb_version or self._kb_index is None:
                entries = list(
                    KnowledgeBase.objects.filter(is_active=True)
                    .order_by('-priority', 'question')
                    .values('question', 'answer', 'keywords')
                )
                if not entries:
                    return None
                texts = [e['question'] for e in entries]
                embeddings = model.encode(texts, convert_to_tensor=True)
                self._kb_index = (embeddings, entries)
                self._kb_version = count
            return self._kb_index
        except Exception as e:
            logger.error(f"KB index build failed: {e}")
            return None

    def _get_faq_index(self, model):
        try:
            from faqs.models import FAQ
            count = FAQ.objects.filter(is_active=True).count()
            if count != self._faq_version or self._faq_index is None:
                entries = list(
                    FAQ.objects.filter(is_active=True)
                    .values('question', 'answer', 'category')
                )
                if not entries:
                    return None
                texts = [e['question'] for e in entries]
                embeddings = model.encode(texts, convert_to_tensor=True)
                self._faq_index = (embeddings, entries)
                self._faq_version = count
            return self._faq_index
        except Exception as e:
            logger.error(f"FAQ index build failed: {e}")
            return None

    # ---- Cosine similarity search ----

    def _cosine_search(self, model, query, embeddings, entries, threshold):
        try:
            import torch
            from sentence_transformers import util as st_util
            query_emb = model.encode(query, convert_to_tensor=True)
            scores = st_util.cos_sim(query_emb, embeddings)[0]
            best_idx = int(scores.argmax())
            best_score = float(scores[best_idx])
            self._last_match_idx = best_idx
            if best_score >= threshold:
                return entries[best_idx]['answer']
        except Exception as e:
            logger.error(f"Cosine search failed: {e}")
        return None

    # ---- Keyword fallbacks ----

    def _keyword_search_kb(self, query: str) -> Optional[str]:
        """Fallback keyword search when sentence-transformers unavailable."""
        try:
            from .models import KnowledgeBase
            entries = KnowledgeBase.objects.filter(is_active=True).order_by('-priority')
            msg_lower = query.lower()
            msg_words = set(re.findall(r'\b\w+\b', msg_lower))
            best, best_score = None, 0
            for entry in entries:
                keywords = entry.keyword_list
                if not keywords:
                    continue
                matched = sum(1 for kw in keywords if kw in msg_lower)
                if matched < 2:
                    continue
                score = matched / len(keywords) + entry.priority * 0.05
                if score > best_score:
                    best_score, best = score, entry
            if best and best_score >= 0.5:
                return best.answer
        except Exception:
            pass
        return None

    def _keyword_search_faq(self, query: str) -> Optional[str]:
        """Fallback keyword search for FAQs."""
        try:
            from faqs.models import FAQ
            stop = {'i','a','an','the','is','are','do','does','what','how','why','when','where'}
            faqs = FAQ.objects.filter(is_active=True)
            msg_words = set(re.findall(r'\b\w+\b', query.lower())) - stop
            best, best_score = None, 0
            for faq in faqs:
                q_words = set(re.findall(r'\b\w+\b', faq.question.lower())) - stop
                if not q_words:
                    continue
                overlap = q_words & msg_words
                score = len(overlap) / max(len(q_words), len(msg_words))
                if score > best_score:
                    best_score, best = score, faq
            if best and best_score >= 0.25:
                return (
                    f"FAQ: {best.question}\n\n{best.answer}\n\n"
                    "Do you have another question? I'm happy to help."
                )
        except Exception:
            pass
        return None


# ------------------------------------------------------------------ #
#  Intent Classifier                                                   #
# ------------------------------------------------------------------ #

class IntentClassifier:
    """
    Lightweight intent classification using semantic similarity.
    Falls back to keyword scoring if sentence-transformers unavailable.
    """

    INTENT_EXAMPLES = {
        'greeting':         ["hello", "hi there", "good morning", "hey", "greetings"],
        'goodbye':          ["bye", "goodbye", "see you later", "thanks bye", "farewell"],
        'property_search':  ["show me properties", "find a house", "looking for apartment", "available listings", "search homes"],
        'property_details': ["tell me about this property", "details on the house", "what are the features", "describe the property"],
        'pricing':          ["how much does it cost", "what is the price", "budget range", "affordable homes", "under 500000"],
        'location':         ["properties in Sydney", "homes near the beach", "what areas do you cover", "which cities"],
        'schedule_viewing': ["I want to visit", "schedule a tour", "book a viewing", "can I see the property"],
        'contact':          ["how do I contact you", "agent phone number", "email address", "speak to someone"],
        'sell_property':    ["I want to sell my house", "list my property", "how to sell", "selling my home"],
        'rent':             ["looking to rent", "rental properties", "lease an apartment", "monthly rent"],
        'mortgage':         ["home loan", "mortgage rates", "financing options", "pre-approval", "bank loan"],
        'investment':       ["investment property", "rental yield", "portfolio growth", "ROI", "passive income"],
        'help':             ["what can you do", "help me", "how does this work", "what are your services"],
    }

    def __init__(self):
        self._intent_embeddings = None
        self._intent_labels = None

    def classify(self, text: str) -> tuple[str, float]:
        """Returns (intent, confidence)."""
        model = _get_sentence_model()
        if model:
            return self._semantic_classify(model, text)
        return self._keyword_classify(text)

    def _semantic_classify(self, model, text: str) -> tuple[str, float]:
        try:
            from sentence_transformers import util as st_util
            if self._intent_embeddings is None:
                self._intent_labels = []
                all_examples = []
                for intent, examples in self.INTENT_EXAMPLES.items():
                    for ex in examples:
                        self._intent_labels.append(intent)
                        all_examples.append(ex)
                self._intent_embeddings = model.encode(all_examples, convert_to_tensor=True)

            query_emb = model.encode(text, convert_to_tensor=True)
            scores = st_util.cos_sim(query_emb, self._intent_embeddings)[0]
            best_idx = int(scores.argmax())
            best_score = float(scores[best_idx])

            if best_score >= 0.30:
                return self._intent_labels[best_idx], round(best_score, 3)
        except Exception as e:
            logger.error(f"Semantic classify failed: {e}")

        return self._keyword_classify(text)

    def _keyword_classify(self, text: str) -> tuple[str, float]:
        """Keyword-based fallback."""
        keyword_map = {
            'property_search':  ['property', 'house', 'home', 'apartment', 'find', 'show', 'available', 'listing', 'buy', 'purchase'],
            'property_details': ['detail', 'information', 'tell', 'about', 'describe', 'feature'],
            'pricing':          ['price', 'cost', 'budget', 'afford', 'cheap', 'expensive', 'range'],
            'location':         ['location', 'area', 'near', 'city', 'where', 'neighborhood'],
            'schedule_viewing': ['visit', 'viewing', 'tour', 'schedule', 'appointment', 'see'],
            'contact':          ['contact', 'call', 'email', 'agent', 'phone', 'reach'],
            'sell_property':    ['sell', 'selling', 'list my', 'market my'],
            'rent':             ['rent', 'rental', 'lease', 'tenant'],
            'mortgage':         ['mortgage', 'loan', 'financing', 'bank', 'interest'],
            'investment':       ['invest', 'portfolio', 'roi', 'yield', 'income', 'wealth'],
            'greeting':         ['hello', 'hi', 'hey', 'morning', 'afternoon', 'evening'],
            'goodbye':          ['bye', 'goodbye', 'thanks', 'thank you'],
            'help':             ['help', 'assist', 'support', 'faq', 'what can'],
        }
        text_lower = text.lower()
        scores = {}
        for intent, keywords in keyword_map.items():
            score = sum(1.5 if kw in text_lower else 0 for kw in keywords)
            scores[intent] = score

        if scores:
            best = max(scores, key=scores.get)
            if scores[best] > 0:
                return best, min(scores[best] / 5.0, 0.85)

        return 'general', 0.5

    def analyze_sentiment(self, text: str) -> dict:
        """Simple rule-based sentiment (no external deps)."""
        positive = ['great', 'good', 'excellent', 'perfect', 'love', 'amazing', 'wonderful', 'fantastic', 'happy', 'pleased']
        negative = ['bad', 'terrible', 'awful', 'hate', 'disappointed', 'frustrated', 'angry', 'poor', 'worst', 'horrible']
        text_lower = text.lower()
        pos = sum(1 for w in positive if w in text_lower)
        neg = sum(1 for w in negative if w in text_lower)
        compound = (pos - neg) / max(pos + neg, 1) if (pos + neg) > 0 else 0
        return {'compound': compound, 'pos': pos, 'neg': neg, 'neu': 1 - abs(compound)}
