"""
Modern Local NLP Engine
========================
Replaces brittle NLTK keyword matching with:
  - spaCy en_core_web_sm  → NER (locations, money, cardinal numbers)
  - sentence-transformers  → semantic vector search for KB & FAQ
  - Regex fallbacks        → budget / bedroom extraction

All processing is 100% local — no external API calls.
"""

from __future__ import annotations

import re
import threading
from functools import lru_cache
from typing import Optional

import numpy as np

# ------------------------------------------------------------------ #
#  Lazy singletons — loaded once, reused across requests              #
# ------------------------------------------------------------------ #

_spacy_nlp = None
_st_model   = None
_lock       = threading.Lock()


def _get_spacy():
    global _spacy_nlp
    if _spacy_nlp is None:
        with _lock:
            if _spacy_nlp is None:
                try:
                    import spacy
                    _spacy_nlp = spacy.load("en_core_web_sm")
                except Exception:
                    _spacy_nlp = False   # mark as unavailable
    return _spacy_nlp if _spacy_nlp else None


def _get_st():
    global _st_model
    if _st_model is None:
        with _lock:
            if _st_model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                    # all-MiniLM-L6-v2 is tiny (80 MB) and fast
                    _st_model = SentenceTransformer("all-MiniLM-L6-v2")
                except Exception:
                    _st_model = False
    return _st_model if _st_model else None


# ------------------------------------------------------------------ #
#  spaCy NER extraction                                               #
# ------------------------------------------------------------------ #

class SpacyExtractor:
    """
    Extracts structured entities from free-text using spaCy NER.
    Falls back to regex when spaCy is unavailable.
    """

    # ---- Budget ----

    def extract_budget(self, text: str) -> Optional[int]:
        nlp = _get_spacy()
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "MONEY":
                    val = self._parse_money(ent.text)
                    if val:
                        return val
        # Regex fallback
        return self._regex_budget(text)

    def _parse_money(self, text: str) -> Optional[int]:
        text = text.lower().replace(",", "").replace("$", "").strip()
        multipliers = {"k": 1_000, "m": 1_000_000, "million": 1_000_000, "thousand": 1_000}
        for suffix, mult in multipliers.items():
            m = re.search(rf"([\d.]+)\s*{suffix}", text)
            if m:
                return int(float(m.group(1)) * mult)
        m = re.search(r"[\d.]+", text)
        if m:
            val = float(m.group())
            return int(val * 1000 if val < 1000 else val)
        return None

    def _regex_budget(self, text: str) -> Optional[int]:
        patterns = [
            (r"\$?([\d,]+)\s*(?:million|m)\b", 1_000_000),
            (r"\$?([\d,]+)\s*k\b",             1_000),
            (r"\$?([\d,]+),000\b",             1_000),
            (r"\$?([\d]{4,})\b",               1),
        ]
        for pat, mult in patterns:
            m = re.search(pat, text.lower())
            if m:
                return int(m.group(1).replace(",", "")) * mult
        return None

    # ---- Bedrooms ----

    def extract_beds(self, text: str) -> Optional[int]:
        nlp = _get_spacy()
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "CARDINAL":
                    # Check if next token is bedroom-related
                    end = ent.end
                    if end < len(doc):
                        nxt = doc[end].text.lower()
                        if any(w in nxt for w in ["bed", "br", "room"]):
                            try:
                                return int(ent.text)
                            except ValueError:
                                pass
        # Regex fallback
        m = re.search(r"(\d+)\s*(?:bed|bedroom|br)\b", text.lower())
        return int(m.group(1)) if m else None

    # ---- City / Location ----

    def extract_city(self, text: str, known_cities: list[str]) -> Optional[str]:
        """
        First try spaCy GPE (geo-political entity) NER,
        then fall back to substring match against known DB cities.
        """
        nlp = _get_spacy()
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ("GPE", "LOC"):
                    # Check if it matches a known city
                    for city in known_cities:
                        if city.lower() == ent.text.lower():
                            return city
        # Substring fallback
        msg_lower = text.lower()
        for city in known_cities:
            if city.lower() in msg_lower:
                return city
        return None

    # ---- Property type ----

    def extract_property_type(self, text: str) -> Optional[str]:
        types = ["apartment", "house", "villa", "condo", "land", "plot",
                 "flat", "studio", "townhouse", "duplex", "penthouse"]
        msg_lower = text.lower()
        for pt in types:
            if pt in msg_lower:
                return pt.upper()
        return None

    # ---- Full entity extraction ----

    def extract_all(self, text: str, known_cities: list[str]) -> dict:
        return {
            "budget":        self.extract_budget(text),
            "beds":          self.extract_beds(text),
            "city":          self.extract_city(text, known_cities),
            "property_type": self.extract_property_type(text),
        }


# ------------------------------------------------------------------ #
#  Semantic Vector Search                                             #
# ------------------------------------------------------------------ #

class SemanticSearcher:
    """
    Encodes Knowledge Base / FAQ entries into vectors once,
    then uses cosine similarity to find the best match for any query.

    Vectors are cached in memory and invalidated when DB changes.
    """

    def __init__(self):
        self._kb_cache:   dict = {}   # {entry_id: vector}
        self._faq_cache:  dict = {}
        self._kb_texts:   dict = {}   # {entry_id: answer}
        self._faq_texts:  dict = {}   # {faq_id: answer}
        self._lock = threading.Lock()

    # ---- Cosine similarity ----

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        return float(np.dot(a, b) / denom) if denom > 0 else 0.0

    # ---- Encode query ----

    def _encode(self, text: str) -> Optional[np.ndarray]:
        model = _get_st()
        if not model:
            return None
        return model.encode(text, convert_to_numpy=True)

    # ---- Knowledge Base search ----

    def search_kb(self, query: str, threshold: float = 0.45) -> Optional[str]:
        """
        Returns the best-matching KB answer if similarity ≥ threshold.
        """
        model = _get_st()
        if not model:
            return None

        try:
            from .models import KnowledgeBase
            entries = list(KnowledgeBase.objects.filter(is_active=True).order_by("-priority"))
            if not entries:
                return None

            q_vec = self._encode(query)
            if q_vec is None:
                return None

            best_score = 0.0
            best_answer = None

            for entry in entries:
                # Build combined text for embedding
                combined = f"{entry.question} {entry.answer[:200]}"
                eid = entry.id

                with self._lock:
                    if eid not in self._kb_cache:
                        self._kb_cache[eid] = model.encode(combined, convert_to_numpy=True)
                    vec = self._kb_cache[eid]

                score = self._cosine(q_vec, vec)
                # Boost by priority
                score += entry.priority * 0.01

                if score > best_score:
                    best_score = score
                    best_answer = entry.answer

            return best_answer if best_score >= threshold else None

        except Exception:
            return None

    # ---- FAQ search ----

    def search_faq(self, query: str, threshold: float = 0.40) -> Optional[str]:
        """
        Returns the best-matching FAQ answer if similarity ≥ threshold.
        """
        model = _get_st()
        if not model:
            return None

        try:
            from faqs.models import FAQ
            faqs = list(FAQ.objects.filter(is_active=True))
            if not faqs:
                return None

            q_vec = self._encode(query)
            if q_vec is None:
                return None

            best_score = 0.0
            best_faq = None

            for faq in faqs:
                fid = faq.id
                with self._lock:
                    if fid not in self._faq_cache:
                        self._faq_cache[fid] = model.encode(faq.question, convert_to_numpy=True)
                    vec = self._faq_cache[fid]

                score = self._cosine(q_vec, vec)
                if score > best_score:
                    best_score = score
                    best_faq = faq

            if best_faq and best_score >= threshold:
                return (
                    f"FAQ: {best_faq.question}\n\n"
                    f"{best_faq.answer}\n\n"
                    f"Category: {best_faq.category}\n\n"
                    "Do you have another question? I'm happy to help."
                )
            return None

        except Exception:
            return None

    def invalidate_kb(self):
        """Call after admin saves a KB entry."""
        with self._lock:
            self._kb_cache.clear()

    def invalidate_faq(self):
        """Call after admin saves a FAQ entry."""
        with self._lock:
            self._faq_cache.clear()


# ------------------------------------------------------------------ #
#  Module-level singletons                                            #
# ------------------------------------------------------------------ #

extractor = SpacyExtractor()
searcher  = SemanticSearcher()
