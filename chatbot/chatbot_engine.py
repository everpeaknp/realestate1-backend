"""
Chatbot Engine v2 — Modern Local NLP Stack
==========================================
Priority chain (first match wins):
  0. Chatbot Rules        — admin-managed exact/regex patterns
  1. Property Name Match  — direct title/slug lookup
  2. Knowledge Base       — semantic vector search (sentence-transformers)
  3. FAQ                  — semantic vector search (sentence-transformers)
  4. Intent Handlers      — spaCy NER + NLTK intent detection

100% local — no external API calls.
"""

from __future__ import annotations

import random
import re

from django.conf import settings
from django.core.cache import cache

from .models import ChatbotRule, KnowledgeBase
from .nlp_engine import extractor, searcher
from properties.models import ExternalPropertyFeed, Property
from faqs.models import FAQ


class ChatbotEngine:
    """Main chatbot engine — orchestrates the NLP pipeline."""
    SEARCH_PAGE_SIZE = 8
    SEARCH_CACHE_TTL_SECONDS = 1800

    def __init__(self):
        # Keep NLTK processor as intent fallback
        try:
            from .nltk_processor import NLTKProcessor
            self.nlp = NLTKProcessor()
        except Exception:
            self.nlp = None

    # ---------------------------------------------------------------- #
    #  Public entry point                                               #
    # ---------------------------------------------------------------- #

    def process_message(self, message: str, session_id: str | None = None) -> dict:
        if self._is_show_more_request(message):
            response = self._handle_show_more(session_id)
            if response:
                sentiment = self._analyze_sentiment(message)
                return self._result(response, "property_search", 0.95, sentiment)

        intent, confidence = self._detect_intent(message)
        sentiment = self._analyze_sentiment(message)
        extracted_budget = extractor.extract_budget(message)
        budget_only_query = self._looks_like_budget_query(message, extracted_budget)

        # Budget-only queries should bypass generic rules/KB and go to property search.
        if budget_only_query:
            response = self._handle_property_search(message, sentiment, session_id=session_id)
            return self._result(response, "property_search", 0.95, sentiment)

        # 0. Rule-based — ABSOLUTE HIGHEST PRIORITY
        rule_response = self._match_rule(message)
        if rule_response:
            return self._result(rule_response, "rule_match", 1.0, sentiment)

        # 1. Specific property name match
        prop_response = self._check_property_match(message)
        if prop_response:
            return self._result(prop_response, "property_details", 0.98, sentiment)

        # 1.5. Property search priority check
        # If user clearly wants to SEE/FIND properties (not SELL), skip KB/FAQ
        msg_lower = message.lower()
        property_search_indicators = [
            # GENERIC PROPERTY SEARCH
            "property", "properties", "real estate", "realestate", "listing", "listings",
            "property listings", "real estate listings", "available properties", "available homes",
            "show properties", "list properties", "browse properties", "find properties",
            "search properties", "explore properties", "view properties", "show listings",
            "show all properties", "show all listings", "list all properties", "all properties",
            "featured properties", "featured homes", "new listings", "latest listings",
            "active listings", "open listings", "property catalog", "property inventory",
            "available real estate", "property options", "housing options",
            # BUY / PURCHASE INTENT
            "buy property", "buy properties", "buy house", "buy home", "buy apartment",
            "buy flat", "buy villa", "buy townhouse", "buy condo", "buy land",
            "purchase property", "purchase house", "purchase home", "purchase apartment",
            "looking to buy", "want to buy", "interested in buying", "need to buy house",
            "first home buyer", "investment purchase", "homes for sale", "houses for sale",
            "apartments for sale", "villas for sale", "townhouses for sale", "units for sale",
            "land for sale", "commercial property for sale",
            # RENT / LEASE INTENT
            "rent property", "rent house", "rent apartment", "rent flat", "rent home",
            "rental properties", "rental homes", "homes for rent", "houses for rent",
            "apartments for rent", "units for rent", "flats for rent", "lease property",
            "lease apartment", "looking to rent", "want to rent", "need rental",
            "find rentals", "cheap rentals", "family rental", "student accommodation",
            # PROPERTY TYPES
            "house", "houses", "home", "homes", "apartment", "apartments", "flat", "flats",
            "unit", "units", "villa", "villas", "townhouse", "townhouses", "condo", "condos",
            "studio apartment", "penthouse", "duplex", "bungalow", "granny flat", "acreage",
            "farm house", "land", "plot", "plots", "commercial property", "office space",
            "warehouse", "retail space", "industrial property", "coworking space", "restaurant space",
            # AUSTRALIA LOCATIONS
            "australia", "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast",
            "canberra", "hobart", "darwin", "newcastle", "geelong", "wollongong", "sunshine coast",
            "nsw", "new south wales", "victoria", "vic", "queensland", "qld", "western australia",
            "wa", "south australia", "sa", "tasmania", "tas", "northern territory", "nt", "act",
            "parramatta", "blacktown", "liverpool", "bondi", "chatswood", "hurstville",
            "bankstown", "penrith", "campbelltown", "mascot", "southbank", "st kilda",
            "box hill", "richmond", "dandenong", "footscray", "carlton", "clayton",
            # LOCATION PHRASES
            "in sydney", "in melbourne", "in brisbane", "in perth", "in adelaide", "in australia",
            "near me", "nearby properties", "homes nearby", "houses near me", "apartments near me",
            "property near me", "close to city", "city view property", "beachfront property",
            # BUDGET / PRICE
            "under", "below", "above", "within budget", "cheap properties", "affordable homes",
            "budget homes", "luxury homes", "premium properties", "high end homes",
            "million dollar homes", "under 500k", "under 1 million", "under 2 million",
            "under 3 million", "cheap apartments", "low budget rentals", "investment property",
            # BEDROOM/BATHROOM QUERIES
            "1 bedroom", "2 bedroom", "3 bedroom", "4 bedroom", "5 bedroom",
            "1 bed", "2 bed", "3 bed", "4 bed", "5 bed",
            "1 bhk", "2 bhk", "3 bhk", "4 bhk", "studio", "family house",
            "1 bathroom", "2 bathroom", "3 bathroom", "ensuite", "multiple bathrooms",
            # FEATURES / AMENITIES
            "parking", "garage", "double garage", "garden", "backyard", "pool", "swimming pool",
            "gym", "lift", "elevator", "balcony", "rooftop", "pet friendly", "family friendly",
            "furnished", "fully furnished", "semi furnished", "unfurnished", "modern kitchen",
            "renovated", "newly built", "ready to move", "smart home", "gated community",
            "security system",
            # INVESTMENT / COMMERCIAL
            "investment properties", "roi properties", "rental yield", "commercial investment",
            "office investment", "business property", "warehouse for sale", "retail investment",
            "passive income property",
            # NATURAL LANGUAGE QUERIES
            "i need a house", "i need a home", "i need apartment", "i want property",
            "i want house", "show me homes", "show me houses", "show me apartments",
            "show me rentals", "find me a property", "help me find home", "recommend homes",
            "recommend apartments", "looking for family home", "looking for investment property",
            "need luxury apartment", "search property for me", "find dream home", "show best properties",
        ]
        if any(indicator in msg_lower for indicator in property_search_indicators):
            # Skip KB/FAQ and go directly to property search
            response = self._handle_property_search(message, sentiment, session_id=session_id)
            return self._result(response, "property_search", 0.95, sentiment)

        # 2. Knowledge Base — semantic search
        kb_response = searcher.search_kb(message)
        if kb_response:
            return self._result(kb_response, "knowledge_base", 0.95, sentiment)

        # 3. FAQ — semantic search
        faq_response = searcher.search_faq(message)
        if faq_response:
            return self._result(faq_response, "faq_match", 0.90, sentiment)

        # 4. Intent handlers with spaCy NER
        response = self._generate_response(intent, message, sentiment, session_id=session_id)
        return self._result(response, intent, confidence, sentiment)

    # ---------------------------------------------------------------- #
    #  Helpers                                                          #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _result(response, intent, confidence, sentiment):
        return {
            "response":   response,
            "intent":     intent,
            "confidence": confidence,
            "sentiment":  sentiment,
        }

    def _detect_intent(self, message: str) -> tuple[str, float]:
        if self.nlp:
            try:
                return self.nlp.detect_intent(message)
            except Exception:
                pass
        return self._regex_intent(message), 0.6

    def _analyze_sentiment(self, message: str) -> dict:
        if self.nlp:
            try:
                return self.nlp.analyze_sentiment(message)
            except Exception:
                pass
        return {"compound": 0.0}

    def _regex_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return "greeting"
        if any(w in msg for w in ["bye", "goodbye", "thanks", "thank you"]):
            return "goodbye"
        if any(w in msg for w in ["buy", "purchase", "for sale", "looking for", "find", "search", "show"]):
            return "property_search"
        if any(w in msg for w in ["price", "cost", "budget", "afford", "how much"]):
            return "pricing"
        if any(w in msg for w in ["rent", "rental", "lease"]):
            return "rent"
        if any(w in msg for w in ["sell", "selling", "list my"]):
            return "sell_property"
        if any(w in msg for w in ["mortgage", "loan", "finance", "home loan"]):
            return "mortgage"
        if any(w in msg for w in ["invest", "portfolio", "yield", "return"]):
            return "investment"
        if any(w in msg for w in ["contact", "agent", "call", "email", "phone"]):
            return "contact"
        if any(w in msg for w in ["view", "visit", "tour", "schedule", "appointment"]):
            return "schedule_viewing"
        if any(w in msg for w in ["where", "location", "city", "area", "suburb"]):
            return "location"
        if any(w in msg for w in ["help", "what can", "how do", "faq"]):
            return "help"
        return "general"

    def _known_cities(self) -> list[str]:
        cities = set(Property.objects.values_list("city", flat=True).distinct())
        if self._use_reaxml_source():
            suburbs = ExternalPropertyFeed.objects.filter(is_active=True).values_list("suburb", flat=True).distinct()
            for suburb in suburbs:
                if suburb:
                    cities.add(suburb)
        return sorted([city for city in cities if city])

    def _use_reaxml_source(self) -> bool:
        return getattr(settings, "PROPERTY_FEED_SOURCE", "EAGLE_API").strip().upper() == "REAXML"

    def _extract_budget_bounds(self, message: str, extracted_budget: int | None) -> tuple[int | None, int | None]:
        """
        Parse common range phrases like:
          - "1200000 to 1500000"
          - "between 1.2m and 1.5m"
        Returns (min_budget, max_budget). For single budget, max is set.
        """
        def _parse_amount(token: str) -> int | None:
            cleaned = token.lower().replace(",", "").replace("$", "").strip()
            multiplier = 1
            if cleaned.endswith("m"):
                multiplier = 1_000_000
                cleaned = cleaned[:-1]
            elif cleaned.endswith("k"):
                multiplier = 1_000
                cleaned = cleaned[:-1]
            try:
                return int(float(cleaned) * multiplier)
            except (TypeError, ValueError):
                return None

        range_match = re.search(
            r"(?:between\s+)?([$]?\d[\d,]*(?:\.\d+)?[mk]?)\s*(?:to|-|and)\s*([$]?\d[\d,]*(?:\.\d+)?[mk]?)",
            message.lower(),
        )
        if range_match:
            first = _parse_amount(range_match.group(1))
            second = _parse_amount(range_match.group(2))
            if first and second:
                return (min(first, second), max(first, second))

        if extracted_budget is None:
            return (None, None)

        msg = message.lower()
        if re.search(r"\b(around|about|approx(?:\.|imately)?)\b", msg):
            lower = int(extracted_budget * 0.85)
            upper = int(extracted_budget * 1.15)
            return (lower, upper)

        if re.search(r"\b(over|above|from|min(?:imum)?)\b", msg):
            return (extracted_budget, None)

        return (None, extracted_budget)

    def _looks_like_budget_query(self, message: str, extracted_budget: int | None) -> bool:
        if extracted_budget is None:
            return False

        msg = message.strip().lower()
        if re.fullmatch(r"[$\s\d,.\-mk]+", msg):
            return True

        budget_terms = [
            "around",
            "about",
            "approx",
            "approximately",
            "under",
            "below",
            "between",
            "budget",
            "to",
            "-",
        ]
        return any(term in msg for term in budget_terms)

    def _is_show_more_request(self, message: str) -> bool:
        msg = message.strip().lower()
        return bool(
            re.fullmatch(
                r"(show\s+me\s+more|show\s+more(?:\s+properties)?|more|next(?:\s+properties|\s+page)?)",
                msg,
            )
        )

    def _search_cache_key(self, session_id: str) -> str:
        return f"chatbot_property_search_{session_id}"

    def _remember_search(self, session_id: str | None, properties: list[dict], filter_str: str) -> None:
        if not session_id or not properties:
            return
        cache.set(
            self._search_cache_key(session_id),
            {
                "properties": properties,
                "offset": self.SEARCH_PAGE_SIZE,
                "filter_str": filter_str,
            },
            timeout=self.SEARCH_CACHE_TTL_SECONDS,
        )

    def _handle_show_more(self, session_id: str | None) -> str | None:
        if not session_id:
            return (
                "I can show more only in the same chat session. "
                "Please search again and then reply 'show more properties'."
            )

        payload = cache.get(self._search_cache_key(session_id))
        if not payload:
            return (
                "No recent property results to continue. "
                "Tell me your budget or suburb and I will search again."
            )

        properties = payload.get("properties") or []
        offset = int(payload.get("offset", self.SEARCH_PAGE_SIZE))
        filter_str = payload.get("filter_str", "")

        if offset >= len(properties):
            cache.delete(self._search_cache_key(session_id))
            return "You've seen all matching properties. Try a new budget or suburb."

        chunk = properties[offset: offset + self.SEARCH_PAGE_SIZE]
        response = f"Here are more properties{filter_str}:\n\n"
        for prop in chunk:
            response += self._format_eagle_property(prop) + "\n\n"

        new_offset = offset + len(chunk)
        remaining = max(len(properties) - new_offset, 0)
        if remaining > 0:
            payload["offset"] = new_offset
            cache.set(self._search_cache_key(session_id), payload, timeout=self.SEARCH_CACHE_TTL_SECONDS)
            response += f"I can show {remaining} more matching properties. Reply 'show more properties'."
        else:
            cache.delete(self._search_cache_key(session_id))
            response += "That's all matching properties for now. Want to refine your search?"
        return response

    def _sort_property_dicts_by_budget(self, properties: list[dict], target_budget: float) -> list[dict]:
        def _distance(prop: dict) -> tuple[float, float]:
            try:
                price = float(prop.get("price"))
            except (TypeError, ValueError):
                return (float("inf"), 0.0)
            return (abs(price - target_budget), -price)

        return sorted(properties, key=_distance)

    def _build_property_search_response(
        self,
        results: list[dict],
        filter_str: str,
        session_id: str | None,
    ) -> str:
        page = results[: self.SEARCH_PAGE_SIZE]
        response = f"Here are some properties{filter_str}:\n\n"
        for prop in page:
            response += self._format_eagle_property(prop) + "\n\n"

        remaining = max(len(results) - len(page), 0)
        if remaining > 0:
            self._remember_search(session_id, results, filter_str)
            response += f"I can show {remaining} more matching properties. Reply 'show more properties'."
        else:
            response += "Would you like more details on any of these? Just ask!"
        return response

    def _dedupe_property_dicts(self, properties: list[dict], max_items: int = 40) -> list[dict]:
        unique: list[dict] = []
        seen: set[tuple[str, str, str]] = set()

        for prop in properties:
            key = (
                str(prop.get("headline", "")).strip().lower(),
                str(prop.get("formattedAddress", "")).strip().lower(),
                str(prop.get("price", "")),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(prop)
            if len(unique) >= max_items:
                break
        return unique

    # ---------------------------------------------------------------- #
    #  Rule matching                                                    #
    # ---------------------------------------------------------------- #

    def _match_rule(self, message: str) -> str | None:
        try:
            for rule in ChatbotRule.objects.filter(is_active=True).order_by("-priority", "name"):
                if rule.matches(message):
                    return rule.response
        except Exception:
            pass
        return None

    # ---------------------------------------------------------------- #
    #  Property name match                                              #
    # ---------------------------------------------------------------- #

    def _check_property_match(self, message: str) -> str | None:
        try:
            msg_lower = message.lower()
            detail_kw = ["detail", "about", "tell me", "show me", "info", "information"]
            has_detail = any(kw in msg_lower for kw in detail_kw)
            for prop in Property.objects.filter(status="AVAILABLE"):
                if prop.title.lower() in msg_lower or prop.slug.replace("-", " ") in msg_lower:
                    if has_detail or len(msg_lower.split()) <= 5:
                        return self._format_property_details(prop)
        except Exception:
            pass
        return None

    # ---------------------------------------------------------------- #
    #  Intent dispatch                                                  #
    # ---------------------------------------------------------------- #

    def _generate_response(self, intent: str, message: str, sentiment: dict, session_id: str | None = None) -> str:
        handlers = {
            "greeting":         self._handle_greeting,
            "goodbye":          self._handle_goodbye,
            "property_search":  self._handle_property_search,
            "property_details": self._handle_property_details,
            "pricing":          self._handle_pricing,
            "location":         self._handle_location,
            "schedule_viewing": self._handle_schedule_viewing,
            "contact":          self._handle_contact,
            "sell_property":    self._handle_sell_property,
            "rent":             self._handle_rent,
            "mortgage":         self._handle_mortgage,
            "investment":       self._handle_investment,
            "help":             self._handle_help,
            "general":          self._handle_general,
        }
        handler = handlers.get(intent, self._handle_general)
        if intent in {"property_search", "general"}:
            return handler(message, sentiment, session_id=session_id)
        return handler(message, sentiment)

    # ---------------------------------------------------------------- #
    #  Formatters                                                       #
    # ---------------------------------------------------------------- #

    def _format_property(self, prop, include_link=True) -> str:
        ptype = "For Sale" if prop.property_type == "FOR_SALE" else "For Rent"
        lines = [
            f"PROPERTY: {prop.title}",
            f"Price: ${prop.price:,.0f} ({ptype})",
            f"Details: {prop.beds} bed | {prop.baths} bath | {prop.sqft:,} sqft",
            f"Location: {prop.city}, {prop.state}",
        ]
        if include_link:
            lines.append(f"View Property: /properties/{prop.slug}")
        lines.append("")
        return "\n".join(lines)

    def _format_eagle_property(self, prop: dict) -> str:
        """Format Eagle API property for chatbot response."""
        import re
        
        # Extract property details from Eagle API format
        headline = prop.get('headline', 'Property').strip()
        price = prop.get('price', 0)
        property_type = prop.get('propertyType', 'Property')
        formatted_address = prop.get('formattedAddress', 'Location not specified')
        description = prop.get('description', '')
        
        # Prefer structured fields when present (REAXML source), then fallback to regex parsing.
        bedrooms = prop.get("bedrooms") or prop.get("beds") or 0
        bathrooms = prop.get("bathrooms") or prop.get("baths") or 0
        parking = prop.get("garages") or prop.get("cars") or 0

        if not bedrooms:
            bed_match = re.search(r'(\d+)\s*(?:Spacious\s+)?(?:Bedroom|bed|BR)', description, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))

        if not bathrooms:
            bath_match = re.search(r'(\d+)\s*(?:Modern\s+)?(?:Bathroom|bath|BA)', description, re.IGNORECASE)
            if bath_match:
                bathrooms = int(bath_match.group(1))

        if not parking:
            parking_patterns = [
                r'Double\s+Car\s+Garage',  # Double Car Garage
                r'(\d+)\s+Car\s+Garage',   # 2 Car Garage
                r'(\d+)\s+Garage',         # 2 Garage
                r'(\d+)\s+parking',        # 2 parking
            ]
            for pattern in parking_patterns:
                parking_match = re.search(pattern, description, re.IGNORECASE)
                if parking_match:
                    if 'Double' in parking_match.group(0):
                        parking = 2
                    else:
                        parking = int(parking_match.group(1))
                    break
        
        # Format price
        price_str = f"${price:,.0f}" if price > 0 else "Price on request"
        
        # Build details string
        details_parts = []
        if bedrooms > 0:
            details_parts.append(f"{bedrooms} bed")
        if bathrooms > 0:
            details_parts.append(f"{bathrooms} bath")
        if parking > 0:
            details_parts.append(f"{parking} parking")
        
        details = " | ".join(details_parts) if details_parts else "Details not specified"
        
        # Build response
        lines = [
            f"PROPERTY: {headline}",
            f"📍 {formatted_address}",
            f"Price: {price_str}",
            f"Type: {property_type}",
            f"Details: {details}",
        ]
        
        # Add land size if available
        land_size = prop.get('landSize')
        land_units = prop.get('landSizeUnits', 'sqm')
        if land_size:
            lines.append(f"Land: {land_size} {land_units}")
        
        lines.append("")
        return "\n".join(lines)

    def _format_property_details(self, prop) -> str:
        ptype = "For Sale" if prop.property_type == "FOR_SALE" else "For Rent"
        amenities = ", ".join(prop.amenities_list[:5]) if prop.amenities_list else "N/A"
        lines = [
            f"PROPERTY: {prop.title}",
            f"Price: ${prop.price:,.0f} ({ptype})",
            f"Location: {prop.address}, {prop.city}, {prop.state} {prop.zip_code}",
            f"Details: {prop.beds} bed | {prop.baths} bath | {prop.garage} garage",
            f"Size: {prop.sqft:,} sqft" + (f" | Lot: {prop.lot_size:,} sqft" if prop.lot_size else ""),
        ]
        if prop.year_built:
            lines.append(f"Year Built: {prop.year_built}")
        lines.append(f"Features: {amenities}")
        lines.append(f"\nView Property: /properties/{prop.slug}")
        return "\n".join(lines)

    # ---------------------------------------------------------------- #
    #  Intent handlers — now use spaCy NER via extractor               #
    # ---------------------------------------------------------------- #

    def _handle_greeting(self, message, sentiment):
        return random.choice([
            "Hello! I'm here to help you with your property needs. I represent Bijen Khadka, an experienced Investment Property Specialist with 12+ years of experience and 1500+ satisfied clients. How can I assist you today?",
            "Hi there! Welcome to Lily White Real Estate. Whether you're looking to buy, sell, rent, or need investment guidance, I'm here to help. What brings you here today?",
            "Welcome! I'm your property assistant representing Bijen Khadka. With expertise across 24 locations and $85+ million saved for clients, we're here to help you find the perfect solution. What are you looking for?",
        ])

    def _handle_goodbye(self, message, sentiment):
        return random.choice([
            "Thanks for chatting! Feel free to come back anytime. Good luck with your property search!",
            "Goodbye! We're here whenever you need help with your real estate journey.",
            "Have a great day! Don't hesitate to reach out if you have more questions.",
        ])

    def _handle_property_search(self, message, sentiment, session_id: str | None = None):
        """
        Handle property search - tries Eagle API first, then Django DB.
        Eagle API is the primary source since Django DB may be empty.
        """
        import logging

        logger = logging.getLogger(__name__)
        cities = self._known_cities()
        ents = extractor.extract_all(message, cities)
        msg_lower = message.lower()
        budget_min, budget_max = self._extract_budget_bounds(message, ents.get("budget"))
        around_query = bool(re.search(r"\b(around|about|approx(?:\.|imately)?)\b", msg_lower))

        target_budget = None
        if around_query and ents.get("budget") is not None:
            target_budget = float(ents["budget"])
        elif budget_min is not None and budget_max is not None:
            target_budget = (budget_min + budget_max) / 2
        elif budget_max is not None:
            target_budget = float(budget_max)
        elif budget_min is not None:
            target_budget = float(budget_min)

        def _price_value(value):
            try:
                if value is None:
                    return None
                return float(value)
            except (TypeError, ValueError):
                return None

        def _budget_filter_label():
            if budget_min is not None and budget_max is not None:
                return f"${budget_min:,} - ${budget_max:,}"
            if budget_max is not None:
                return f"under ${budget_max:,}"
            if budget_min is not None:
                return f"over ${budget_min:,}"
            return None

        def _filter_str():
            filters = []
            if ents["city"]:
                filters.append(f"in {ents['city']}")
            if ents["beds"]:
                filters.append(f"{ents['beds']}+ bedrooms")
            budget_label = _budget_filter_label()
            if budget_label:
                filters.append(budget_label)
            return f" ({', '.join(filters)})" if filters else ""

        # REAXML source can be read directly from backend DB without relying on frontend proxy.
        if self._use_reaxml_source():
            qs = ExternalPropertyFeed.objects.filter(is_active=True)

            if any(w in msg_lower for w in ["rent", "rental", "lease"]):
                qs = qs.filter(listing_type__in=["RENTAL", "HOLIDAY"])
            elif any(w in msg_lower for w in ["buy", "purchase", "sale", "for sale"]):
                qs = qs.exclude(listing_type__in=["RENTAL", "HOLIDAY"])

            if ents["city"]:
                qs = qs.filter(suburb__iexact=ents["city"])
            if ents["beds"]:
                qs = qs.filter(bedrooms__gte=ents["beds"])
            if budget_min is not None:
                qs = qs.filter(price__gte=budget_min)
            if budget_max is not None:
                qs = qs.filter(price__lte=budget_max)

            candidates = list(qs.order_by("-updated_at")[:80])
            normalized: list[dict] = []
            for listing in candidates:
                normalized.append(
                    {
                        "headline": listing.headline or listing.formatted_address or "Property",
                        "price": _price_value(listing.price) or 0,
                        "propertyType": listing.property_type or listing.listing_type or "Property",
                        "formattedAddress": listing.formatted_address or listing.suburb or "Location not specified",
                        "description": listing.description or "",
                        "bedrooms": listing.bedrooms,
                        "bathrooms": _price_value(listing.bathrooms),
                        "garages": listing.garages,
                        "landSize": listing.land_size,
                        "landSizeUnits": listing.land_size_units or "sqm",
                    }
                )

            if target_budget is not None:
                normalized = self._sort_property_dicts_by_budget(normalized, target_budget)

            results = self._dedupe_property_dicts(normalized, max_items=40)
            if results:
                return self._build_property_search_response(results, _filter_str(), session_id)

            total_feed = ExternalPropertyFeed.objects.filter(is_active=True).count()
            return (
                f"No properties matched those exact criteria.\n\n"
                f"We have {total_feed} active REAXML listings right now. "
                "Try a different suburb, budget, or bedroom count, or say 'show all properties'."
            )

        # Try Eagle API first (primary source)
        try:
            from .eagle_client import get_eagle_client

            eagle_client = get_eagle_client()

            search_parts = []
            if ents["city"]:
                search_parts.append(ents["city"])
            if ents["beds"]:
                search_parts.append(f"{ents['beds']} bedroom")

            search_term = " ".join(search_parts) if search_parts else ""

            property_type = None
            if any(w in msg_lower for w in ["house", "houses"]):
                property_type = "HOUSE"
            elif any(w in msg_lower for w in ["apartment", "apartments", "unit", "units"]):
                property_type = "APARTMENT"
            elif any(w in msg_lower for w in ["townhouse", "townhouses"]):
                property_type = "TOWNHOUSE"
            elif any(w in msg_lower for w in ["villa", "villas"]):
                property_type = "VILLA"

            logger.info(
                "[Chatbot] Searching Eagle API: search_term='%s', property_type=%s",
                search_term,
                property_type,
            )
            eagle_properties = eagle_client.search_properties(
                search_term=search_term,
                limit=60,
                status="ACTIVE",
                property_type=property_type,
            )

            if eagle_properties:
                if budget_min is not None:
                    eagle_properties = [
                        p for p in eagle_properties
                        if (_price_value(p.get("price")) is not None and _price_value(p.get("price")) >= budget_min)
                    ]
                if budget_max is not None:
                    eagle_properties = [
                        p for p in eagle_properties
                        if (_price_value(p.get("price")) is not None and _price_value(p.get("price")) <= budget_max)
                    ]
                if ents["beds"]:
                    eagle_properties = [
                        p for p in eagle_properties
                        if (p.get("bedrooms") or p.get("beds") or 0) >= ents["beds"]
                    ]

                if target_budget is not None:
                    eagle_properties = self._sort_property_dicts_by_budget(eagle_properties, target_budget)

                results = self._dedupe_property_dicts(eagle_properties, max_items=40)
                if results:
                    return self._build_property_search_response(results, _filter_str(), session_id)

                logger.info(
                    "[Chatbot] Eagle API returned %s properties but none matched filters",
                    len(eagle_properties),
                )
                return (
                    f"I found {len(eagle_properties)} properties, but none matched your exact criteria.\n\n"
                    "Try adjusting your budget, bedroom count, or location, or say 'show all properties'."
                )

            logger.info("[Chatbot] Eagle API returned no properties")
        except Exception as e:
            logger.error(f"[Chatbot] Eagle API search failed: {str(e)}")

        # Fallback to Django DB
        qs = Property.objects.filter(status="AVAILABLE")
        if any(w in msg_lower for w in ["rent", "rental", "lease"]):
            qs = qs.filter(property_type="FOR_RENT")
        elif any(w in msg_lower for w in ["buy", "purchase", "sale", "for sale"]):
            qs = qs.filter(property_type="FOR_SALE")

        if ents["beds"]:
            qs = qs.filter(beds__gte=ents["beds"])
        if ents["city"]:
            qs = qs.filter(city__iexact=ents["city"])
        if budget_min is not None:
            qs = qs.filter(price__gte=budget_min)
        if budget_max is not None:
            qs = qs.filter(price__lte=budget_max)

        candidates = list(qs.order_by("-updated_at")[:80])
        normalized = []
        for listing in candidates:
            normalized.append(
                {
                    "headline": listing.title or "Property",
                    "price": _price_value(listing.price) or 0,
                    "propertyType": listing.get_property_type_display() if hasattr(listing, "get_property_type_display") else "Property",
                    "formattedAddress": f"{listing.city}, {listing.state}",
                    "description": listing.description or "",
                    "bedrooms": listing.beds,
                    "bathrooms": _price_value(listing.baths),
                    "garages": listing.garage,
                }
            )

        if target_budget is not None:
            normalized = self._sort_property_dicts_by_budget(normalized, target_budget)

        results = self._dedupe_property_dicts(normalized, max_items=40)
        if results:
            return self._build_property_search_response(results, _filter_str(), session_id)

        total_django = Property.objects.filter(status="AVAILABLE").count()
        return (
            f"No properties matched those exact criteria.\n\n"
            f"We have {total_django} properties in our database. "
            "Try a different city, budget, or bedroom count, or say 'show all properties'.\n\n"
            "Note: Our live property feed may be temporarily unavailable. Please try again in a moment."
        )

    def _handle_property_details(self, message, sentiment):
        msg_lower = message.lower()
        for prop in Property.objects.filter(status="AVAILABLE"):
            if prop.title.lower() in msg_lower or prop.slug.replace("-", " ") in msg_lower:
                return self._format_property_details(prop)
        return (
            "I'd be happy to give you details on any property!\n\n"
            "Try: 'tell me about Beachfront Paradise' or 'show me the Victorian house'."
        )

    def _handle_pricing(self, message, sentiment):
        budget = extractor.extract_budget(message)
        if budget:
            qs = Property.objects.filter(status="AVAILABLE", price__lte=budget).order_by("price")[:4]
            if qs.exists():
                response = f"Properties within your ${budget:,} budget:\n\n"
                for prop in qs:
                    response += self._format_property(prop) + "\n\n"
                return response
            min_price = Property.objects.filter(status="AVAILABLE").order_by("price").values_list("price", flat=True).first()
            return (
                f"No properties found under ${budget:,}.\n\n"
                f"Our most affordable listing starts at ${min_price:,.0f}. Would you like to see it?"
            )
        props = Property.objects.filter(status="AVAILABLE").order_by("price")
        if props.exists():
            return (
                f"PRICE RANGE\n\n"
                f"Our properties range from ${props.first().price:,.0f} to ${props.last().price:,.0f}.\n\n"
                "Tell me your budget and I'll find the best matches for you!"
            )
        return "Tell me your budget and I'll find properties that fit!"

    def _handle_location(self, message, sentiment):
        city = extractor.extract_city(message, self._known_cities())
        if city:
            props = Property.objects.filter(status="AVAILABLE", city__iexact=city)[:4]
            if props.exists():
                response = f"Properties available in {city}:\n\n"
                for prop in props:
                    response += self._format_property(prop) + "\n\n"
                return response
            return f"No available properties in {city} right now. Would you like to see nearby areas?"
        cities = sorted(set(self._known_cities()))
        if cities:
            return (
                f"AVAILABLE LOCATIONS\n\n"
                f"We have properties in: {', '.join(cities)}.\n\n"
                "Which area interests you? I can show you what's available there."
            )
        return "Tell me which city or neighborhood you're interested in!"

    def _handle_schedule_viewing(self, message, sentiment):
        return (
            "SCHEDULE A VIEWING\n\n"
            "I'd be happy to arrange a property viewing for you.\n\n"
            "Contact Bijen Khadka directly:\n\n"
            "Agent: Bijen Khadka\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au\n\n"
            "We'll work around your schedule and arrange a convenient time. Looking forward to showing you the property!"
        )

    def _handle_contact(self, message, sentiment):
        return (
            "CONTACT INFORMATION\n\n"
            "Agent: Bijen Khadka - Investment Property Specialist\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au\n\n"
            "EXPERIENCE:\n"
            "12+ years experience\n"
            "1500+ satisfied clients\n"
            "$85M+ saved for clients\n"
            "Coverage across 24 locations\n\n"
            "Feel free to reach out anytime. We're here to help you achieve your property goals!"
        )

    def _handle_sell_property(self, message, sentiment):
        return (
            "SELLING YOUR PROPERTY\n\n"
            "Thinking of selling? You're in good hands! With 12+ years of experience and $85M+ saved for clients, here's how we can help:\n\n"
            "- Free property valuation and market analysis\n"
            "- Strategic pricing to maximize your return\n"
            "- Professional marketing across all platforms\n"
            "- Expert negotiation backed by proven results\n"
            "- Full support from listing to settlement\n\n"
            "Contact Bijen Khadka for a free consultation:\n\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au"
        )

    def _handle_rent(self, message, sentiment):
        cities = self._known_cities()
        ents = extractor.extract_all(message, cities)
        qs = Property.objects.filter(status="AVAILABLE", property_type="FOR_RENT")
        if ents["beds"]:   qs = qs.filter(beds__gte=ents["beds"])
        if ents["budget"]: qs = qs.filter(price__lte=ents["budget"])
        results = qs[:4]
        if results.exists():
            response = "Here are our available rental properties:\n\n"
            for prop in results:
                response += self._format_property(prop) + "\n\n"
            return response
        return (
            "We have rental properties including apartments, condos, and houses.\n"
            "Tell me your preferred location, budget, or bedroom count and I'll find the right rental for you!"
        )

    def _handle_mortgage(self, message, sentiment):
        return (
            "HOME LOAN ASSISTANCE\n\n"
            "Home loans can be complex, but we're here to guide you through it!\n\n"
            "We can help you with:\n"
            "- Understanding your borrowing capacity\n"
            "- Finding the right loan structure\n"
            "- Connecting with trusted lenders\n"
            "- Pre-approval assistance\n"
            "- Investment loan strategies\n\n"
            "For detailed home loan assistance, contact Bijen:\n\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au"
        )

    def _handle_investment(self, message, sentiment):
        return (
            "INVESTMENT PROPERTY GUIDANCE\n\n"
            "Building a property investment portfolio? You're in the right place!\n\n"
            "With 12+ years of experience and $85M+ saved for clients, we can help you with:\n\n"
            "- Investment property selection and analysis\n"
            "- Portfolio diversification strategies\n"
            "- Rental yield optimization\n"
            "- Tax-effective investment structures\n"
            "- Long-term wealth building through property\n"
            "- Market insights across 24 locations\n\n"
            "Let's discuss your investment goals:\n\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au"
        )

    def _handle_help(self, message, sentiment):
        try:
            faqs = FAQ.objects.filter(is_active=True).order_by("order")
            if faqs.exists():
                categories: dict = {}
                for faq in faqs:
                    categories.setdefault(faq.category, []).append(faq)
                response = "FREQUENTLY ASKED QUESTIONS\n\n"
                for category, items in categories.items():
                    response += f"{category.upper()}\n"
                    for faq in items:
                        response += f"- {faq.question}\n"
                    response += "\n"
                response += "Ask me any of these questions and I'll give you the full answer!"
                return response
        except Exception:
            pass
        return (
            "[help-circle] Here is how I can help you:\n\n"
            "[home] Show me 3 bedroom homes - property search\n"
            "[map-pin] Properties in Los Angeles - search by city\n"
            "[dollar-sign] Under 300000 - search by budget\n"
            "[info] Tell me about a property - property details\n"
            "[calendar] Schedule a viewing - book a tour\n"
            "[user] Contact an agent - get agent info\n"
            "[tag] What are your services - learn about us\n"
            "[help-circle] FAQs - common questions\n\n"
            "What would you like to do?"
        )

    def _handle_general(self, message, sentiment, session_id: str | None = None):
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["all properties", "all listings", "everything", "show me all"]):
            return self._handle_property_search(message, sentiment, session_id=session_id)
        if sentiment.get("compound", 0) < -0.5:
            return (
                "I understand your concern. Let me help you find the right solution. "
                "Could you tell me more about what you're looking for? "
                "With our experience and expertise, we'll work to find the perfect property for you."
            )
        total = Property.objects.filter(status="AVAILABLE").count()
        return (
            f"HOW I CAN HELP\n\n"
            f"I'm here to assist you with all your property needs! We currently have {total} available properties.\n\n"
            "I can help you with:\n"
            "- Buying properties - residential or investment\n"
            "- Selling your property for the best price\n"
            "- Finding rental properties\n"
            "- Investment portfolio guidance\n"
            "- Home loan assistance\n"
            "- Scheduling property visits\n\n"
            "What would you like to know more about?"
        )
