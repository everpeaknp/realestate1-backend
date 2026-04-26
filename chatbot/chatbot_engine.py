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

from .models import ChatbotRule, KnowledgeBase
from .nlp_engine import extractor, searcher
from properties.models import Property
from faqs.models import FAQ


class ChatbotEngine:
    """Main chatbot engine — orchestrates the NLP pipeline."""

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
        intent, confidence = self._detect_intent(message)
        sentiment = self._analyze_sentiment(message)

        # 0. Rule-based — ABSOLUTE HIGHEST PRIORITY
        rule_response = self._match_rule(message)
        if rule_response:
            return self._result(rule_response, "rule_match", 1.0, sentiment)

        # 1. Specific property name match
        prop_response = self._check_property_match(message)
        if prop_response:
            return self._result(prop_response, "property_details", 0.98, sentiment)

        # 2. Knowledge Base — semantic search
        kb_response = searcher.search_kb(message)
        if kb_response:
            return self._result(kb_response, "knowledge_base", 0.95, sentiment)

        # 3. FAQ — semantic search
        faq_response = searcher.search_faq(message)
        if faq_response:
            return self._result(faq_response, "faq_match", 0.90, sentiment)

        # 4. Intent handlers with spaCy NER
        response = self._generate_response(intent, message, sentiment)
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
        return list(Property.objects.values_list("city", flat=True).distinct())

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

    def _generate_response(self, intent: str, message: str, sentiment: dict) -> str:
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
        return handlers.get(intent, self._handle_general)(message, sentiment)

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

    def _handle_property_search(self, message, sentiment):
        cities = self._known_cities()
        ents = extractor.extract_all(message, cities)

        qs = Property.objects.filter(status="AVAILABLE")
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["rent", "rental", "lease"]):
            qs = qs.filter(property_type="FOR_RENT")
        elif any(w in msg_lower for w in ["buy", "purchase", "sale", "for sale"]):
            qs = qs.filter(property_type="FOR_SALE")

        if ents["beds"]:
            qs = qs.filter(beds__gte=ents["beds"])
        if ents["city"]:
            qs = qs.filter(city__iexact=ents["city"])
        if ents["budget"]:
            qs = qs.filter(price__lte=ents["budget"])

        results = qs[:4]
        if results.exists():
            filters = []
            if ents["city"]:   filters.append(f"in {ents['city']}")
            if ents["beds"]:   filters.append(f"{ents['beds']}+ bedrooms")
            if ents["budget"]: filters.append(f"under ${ents['budget']:,}")
            filter_str = f" ({', '.join(filters)})" if filters else ""
            response = f"Here are some properties{filter_str}:\n\n"
            for prop in results:
                response += self._format_property(prop) + "\n\n"
            response += "Would you like more details on any of these? Just ask!"
            return response

        total = Property.objects.filter(status="AVAILABLE").count()
        return (
            f"No properties matched those exact criteria, but we have {total} available listings overall.\n\n"
            "Try a different city, budget, or bedroom count, or say 'show all properties'."
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

    def _handle_general(self, message, sentiment):
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["all properties", "all listings", "everything", "show me all"]):
            return self._handle_property_search(message, sentiment)
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
