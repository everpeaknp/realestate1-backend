"""
Chatbot Engine — trained on live database data.
Uses [icon] markers that the frontend renders as Lucide icons.
"""
from .nltk_processor import NLTKProcessor
from .models import KnowledgeBase, ChatbotRule
from properties.models import Property
from agents.models import Agent
from faqs.models import FAQ
import random
import re


class ChatbotEngine:
    """Main chatbot engine that processes messages and generates responses"""

    def __init__(self):
        self.nlp = NLTKProcessor()

    def process_message(self, message, session_id=None):
        intent, confidence = self.nlp.detect_intent(message)
        entities = self.nlp.extract_entities(message)
        sentiment = self.nlp.analyze_sentiment(message)

        # 0. Rule-based responses — ABSOLUTE HIGHEST PRIORITY
        rule_response = self._match_rule(message)
        if rule_response:
            return {
                'response': rule_response,
                'intent': 'rule_match',
                'confidence': 1.0,
                'sentiment': sentiment,
            }

        # 1. Check for specific property name match BEFORE general matching
        # This prevents FAQs from intercepting property detail requests
        property_response = self._check_property_match(message)
        if property_response:
            return {
                'response': property_response,
                'intent': 'property_details',
                'confidence': 0.98,
                'sentiment': sentiment,
            }

        # 2. Knowledge Base — admin-managed custom Q&A
        kb_response = self._match_knowledge_base(message)
        if kb_response:
            return {
                'response': kb_response,
                'intent': 'knowledge_base',
                'confidence': 0.95,
                'sentiment': sentiment,
            }

        # 3. FAQ matching
        faq_response = self._match_faq(message)
        if faq_response:
            return {
                'response': faq_response,
                'intent': 'faq_match',
                'confidence': 0.9,
                'sentiment': sentiment,
            }

        # 4. Intent-based handlers
        response = self._generate_response(intent, message, entities, sentiment)
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'sentiment': sentiment,
        }

    def _match_rule(self, message):
        """
        Check all active rules in priority order.
        First matching rule wins — returns immediately.
        """
        try:
            rules = ChatbotRule.objects.filter(is_active=True).order_by('-priority', 'name')
            for rule in rules:
                if rule.matches(message):
                    return rule.response
        except Exception:
            pass
        return None

    def _check_property_match(self, message):
        """
        Check if message contains a specific property name.
        This runs BEFORE FAQs to prevent FAQ false positives on property queries.
        Returns formatted property details if match found, else None.
        """
        try:
            msg_lower = message.lower()
            
            # Keywords that indicate property detail request
            detail_keywords = ['detail', 'about', 'tell me', 'show me', 'info', 'information']
            has_detail_keyword = any(kw in msg_lower for kw in detail_keywords)
            
            # Check all available properties
            for prop in Property.objects.filter(status='AVAILABLE'):
                # Check if property title or slug is in the message
                if prop.title.lower() in msg_lower or prop.slug.replace('-', ' ') in msg_lower:
                    # If it's a detail request or just the property name, show details
                    if has_detail_keyword or len(msg_lower.split()) <= 5:
                        return self._format_property_details(prop)
            
        except Exception:
            pass
        
        return None

    def _format_property_details(self, prop):
        """Format detailed property information"""
        ptype = 'For Sale' if prop.property_type == 'FOR_SALE' else 'For Rent'
        amenities = ', '.join(prop.amenities_list[:5]) if prop.amenities_list else 'N/A'
        
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

    def _match_knowledge_base(self, message):
        """
        Match message against admin-managed Knowledge Base entries.
        Checked before FAQs — highest priority source of truth.
        """
        try:
            entries = KnowledgeBase.objects.filter(is_active=True).order_by('-priority', 'question')
            if not entries.exists():
                return None

            msg_lower = message.lower().strip()
            msg_words = set(re.findall(r'\b\w+\b', msg_lower))

            best_entry = None
            best_score = 0

            for entry in entries:
                keywords = entry.keyword_list
                if not keywords:
                    continue

                # Count how many keywords match
                matched_count = sum(
                    1 for kw in keywords
                    if kw in msg_lower or any(kw in w for w in msg_words)
                )

                # Skip if less than 2 keywords matched (avoid single-word false positives)
                if matched_count < 2:
                    continue

                # Normalise by keyword count, boost by priority
                score = (matched_count / len(keywords)) + (entry.priority * 0.05)

                if score > best_score:
                    best_score = score
                    best_entry = entry

            # Require at least 50% keyword match AND minimum 2 keywords
            if best_entry and best_score >= 0.50:
                return best_entry.answer

        except Exception:
            pass

        return None

    def _match_faq(self, message):
        """
        Match the user message against all active FAQs.
        Returns the FAQ answer if a strong match is found, else None.
        """
        try:
            faqs = FAQ.objects.filter(is_active=True)
            if not faqs.exists():
                return None

            msg_lower = message.lower().strip()
            msg_words = set(re.findall(r'\b\w+\b', msg_lower))

            # Stop words to ignore when scoring
            stop = {
                'i', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
                'do', 'does', 'did', 'have', 'has', 'had', 'will', 'would', 'could',
                'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on',
                'with', 'at', 'by', 'from', 'up', 'about', 'into', 'through',
                'what', 'how', 'why', 'when', 'where', 'who', 'which', 'that',
                'this', 'it', 'me', 'my', 'we', 'our', 'you', 'your', 'need',
                'get', 'much', 'long', 'take', 'between', 'difference',
            }

            best_faq = None
            best_score = 0

            for faq in faqs:
                q_lower = faq.question.lower()
                q_words = set(re.findall(r'\b\w+\b', q_lower)) - stop
                msg_sig = msg_words - stop

                if not q_words or not msg_sig:
                    continue

                # Keyword overlap score
                overlap = q_words & msg_sig
                score = len(overlap) / max(len(q_words), len(msg_sig))

                # Bonus: exact substring match
                for word in msg_sig:
                    if len(word) > 4 and word in q_lower:
                        score += 0.15

                if score > best_score:
                    best_score = score
                    best_faq = faq

            # Threshold: require meaningful overlap
            if best_faq and best_score >= 0.25:
                return (
                    f"FAQ: {best_faq.question}\n\n"
                    f"{best_faq.answer}\n\n"
                    f"Category: {best_faq.category}\n\n"
                    "Do you have another question? I'm happy to help."
                )
        except Exception:
            pass

        return None

    def _generate_response(self, intent, message, entities, sentiment):
        handlers = {
            'greeting':         self._handle_greeting,
            'goodbye':          self._handle_goodbye,
            'property_search':  self._handle_property_search,
            'property_details': self._handle_property_details,
            'pricing':          self._handle_pricing,
            'location':         self._handle_location,
            'schedule_viewing': self._handle_schedule_viewing,
            'contact':          self._handle_contact,
            'sell_property':    self._handle_sell_property,
            'rent':             self._handle_rent,
            'mortgage':         self._handle_mortgage,
            'investment':       self._handle_investment,
            'help':             self._handle_help,
            'general':          self._handle_general,
        }
        return handlers.get(intent, self._handle_general)(message, entities, sentiment)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _format_property(self, prop, include_link=True):
        """Format a property card using clean professional text formatting"""
        ptype = 'For Sale' if prop.property_type == 'FOR_SALE' else 'For Rent'
        lines = [
            f"PROPERTY: {prop.title}",
            f"Price: ${prop.price:,.0f} ({ptype})",
            f"Details: {prop.beds} bed | {prop.baths} bath | {prop.sqft:,} sqft",
            f"Location: {prop.city}, {prop.state}",
        ]
        if include_link:
            lines.append(f"View Property: /properties/{prop.slug}")
        lines.append("")  # Add spacing between properties
        return "\n".join(lines)

    def _extract_budget(self, message):
        patterns = [
            (r'\$?([\d,]+)k', 1000),
            (r'\$?([\d,]+),000', 1000),
            (r'\$?([\d]{4,})', 1),
        ]
        for pat, multiplier in patterns:
            m = re.search(pat, message.lower())
            if m:
                val = int(m.group(1).replace(',', '')) * multiplier
                return val
        return None

    def _extract_beds(self, message):
        m = re.search(r'(\d+)\s*(?:bed|bedroom|br)', message.lower())
        return int(m.group(1)) if m else None

    def _extract_city(self, message):
        cities = list(Property.objects.values_list('city', flat=True).distinct())
        msg_lower = message.lower()
        for city in cities:
            if city.lower() in msg_lower:
                return city
        return None

    # ------------------------------------------------------------------ #
    #  Intent handlers                                                     #
    # ------------------------------------------------------------------ #

    def _handle_greeting(self, message, entities, sentiment):
        return random.choice([
            "Hello! I'm here to help you with your property needs. I represent Bijen Khadka, an experienced Investment Property Specialist with 12+ years of experience and 1500+ satisfied clients. How can I assist you today?",
            "Hi there! Welcome to Lily White Real Estate. Whether you're looking to buy, sell, rent, or need investment guidance, I'm here to help. What brings you here today?",
            "Welcome! I'm your property assistant representing Bijen Khadka. With expertise across 24 locations and $85+ million saved for clients, we're here to help you find the perfect solution. What are you looking for?",
        ])

    def _handle_goodbye(self, message, entities, sentiment):
        return random.choice([
            "Thanks for chatting! Feel free to come back anytime. Good luck with your property search!",
            "Goodbye! We're here whenever you need help with your real estate journey.",
            "Have a great day! Don't hesitate to reach out if you have more questions.",
        ])

    def _handle_property_search(self, message, entities, sentiment):
        qs = Property.objects.filter(status='AVAILABLE')
        msg_lower = message.lower()

        if any(w in msg_lower for w in ['rent', 'rental', 'lease']):
            qs = qs.filter(property_type='FOR_RENT')
        elif any(w in msg_lower for w in ['buy', 'purchase', 'sale', 'for sale']):
            qs = qs.filter(property_type='FOR_SALE')

        beds = self._extract_beds(message)
        if beds:
            qs = qs.filter(beds__gte=beds)

        city = self._extract_city(message)
        if city:
            qs = qs.filter(city__iexact=city)

        budget = self._extract_budget(message)
        if budget:
            qs = qs.filter(price__lte=budget)

        results = qs[:4]

        if results.exists():
            filters = []
            if city:
                filters.append(f"in {city}")
            if beds:
                filters.append(f"{beds}+ bedrooms")
            if budget:
                filters.append(f"under ${budget:,}")
            filter_str = f" ({', '.join(filters)})" if filters else ""
            response = f"Here are some properties{filter_str}:\n\n"
            for prop in results:
                response += self._format_property(prop) + "\n\n"
            response += "Would you like more details on any of these? Just ask!"
            return response

        total = Property.objects.filter(status='AVAILABLE').count()
        return (
            f"No properties matched those exact criteria, but we have {total} available listings overall.\n\n"
            "Try a different city, budget, or bedroom count, or say 'show all properties'."
        )

    def _handle_property_details(self, message, entities, sentiment):
        # This handler is now primarily handled by _check_property_match()
        # But keep as fallback for intent-based routing
        msg_lower = message.lower()
        for prop in Property.objects.filter(status='AVAILABLE'):
            if prop.title.lower() in msg_lower or prop.slug.replace('-', ' ') in msg_lower:
                return self._format_property_details(prop)

        return (
            "I'd be happy to give you details on any property!\n\n"
            "Try: 'tell me about Beachfront Paradise' or 'show me the Victorian house'."
        )

    def _handle_pricing(self, message, entities, sentiment):
        budget = self._extract_budget(message)
        if budget:
            qs = Property.objects.filter(status='AVAILABLE', price__lte=budget).order_by('price')[:4]
            if qs.exists():
                response = f"Properties within your ${budget:,} budget:\n\n"
                for prop in qs:
                    response += self._format_property(prop) + "\n\n"
                return response
            min_price = Property.objects.filter(status='AVAILABLE').order_by('price').values_list('price', flat=True).first()
            return (
                f"No properties found under ${budget:,}.\n\n"
                f"Our most affordable listing starts at ${min_price:,.0f}. Would you like to see it?"
            )

        props = Property.objects.filter(status='AVAILABLE').order_by('price')
        if props.exists():
            return (
                f"PRICE RANGE\n\n"
                f"Our properties range from ${props.first().price:,.0f} to ${props.last().price:,.0f}.\n\n"
                "Tell me your budget and I'll find the best matches for you!"
            )
        return "Tell me your budget and I'll find properties that fit!"

    def _handle_location(self, message, entities, sentiment):
        city = self._extract_city(message)
        if city:
            props = Property.objects.filter(status='AVAILABLE', city__iexact=city)[:4]
            if props.exists():
                response = f"Properties available in {city}:\n\n"
                for prop in props:
                    response += self._format_property(prop) + "\n\n"
                return response
            return f"No available properties in {city} right now. Would you like to see nearby areas?"

        cities = sorted(set(
            Property.objects.filter(status='AVAILABLE').values_list('city', flat=True).distinct()
        ))
        if cities:
            return (
                f"AVAILABLE LOCATIONS\n\n"
                f"We have properties in: {', '.join(cities)}.\n\n"
                "Which area interests you? I can show you what's available there."
            )
        return "Tell me which city or neighborhood you're interested in!"

    def _handle_schedule_viewing(self, message, entities, sentiment):
        return (
            "SCHEDULE A VIEWING\n\n"
            "I'd be happy to arrange a property viewing for you.\n\n"
            "Contact Bijen Khadka directly:\n\n"
            "Agent: Bijen Khadka\n"
            "Phone: +600414701721\n"
            "Email: Bijen@lilywhiterealestate.com.au\n\n"
            "We'll work around your schedule and arrange a convenient time. Looking forward to showing you the property!"
        )

    def _handle_contact(self, message, entities, sentiment):
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

    def _handle_sell_property(self, message, entities, sentiment):
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

    def _handle_rent(self, message, entities, sentiment):
        qs = Property.objects.filter(status='AVAILABLE', property_type='FOR_RENT')
        beds = self._extract_beds(message)
        if beds:
            qs = qs.filter(beds__gte=beds)
        budget = self._extract_budget(message)
        if budget:
            qs = qs.filter(price__lte=budget)
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

    def _handle_mortgage(self, message, entities, sentiment):
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

    def _handle_investment(self, message, entities, sentiment):
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

    def _handle_help(self, message, entities, sentiment):
        try:
            faqs = FAQ.objects.filter(is_active=True).order_by('order')
            if faqs.exists():
                # Group by category
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
            "HOW I CAN HELP\n\n"
            "I can assist you with:\n\n"
            "- Finding properties for sale or rent\n"
            "- Budget and pricing questions\n"
            "- Properties by location\n"
            "- Scheduling viewings\n"
            "- Connecting with our agents\n"
            "- Selling your property\n"
            "- Mortgage and financing\n\n"
            "What would you like to know?"
        )

    def _handle_general(self, message, entities, sentiment):
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['all properties', 'all listings', 'everything', 'show me all']):
            return self._handle_property_search(message, entities, sentiment)

        if sentiment.get('compound', 0) < -0.5:
            return (
                "I understand your concern. Let me help you find the right solution. "
                "Could you tell me more about what you're looking for? "
                "With our experience and expertise, we'll work to find the perfect property for you."
            )

        total = Property.objects.filter(status='AVAILABLE').count()
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
