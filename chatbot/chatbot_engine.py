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

        # 1. Knowledge Base — admin-managed custom Q&A
        kb_response = self._match_knowledge_base(message)
        if kb_response:
            return {
                'response': kb_response,
                'intent': 'knowledge_base',
                'confidence': 0.95,
                'sentiment': sentiment,
            }

        # 2. FAQ matching
        faq_response = self._match_faq(message)
        if faq_response:
            return {
                'response': faq_response,
                'intent': 'faq_match',
                'confidence': 0.9,
                'sentiment': sentiment,
            }

        # 3. Intent-based handlers
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
                    f"[help-circle] {best_faq.question}\n\n"
                    f"{best_faq.answer}\n\n"
                    f"[tag] Category: {best_faq.category}\n"
                    "Do you have another question? I'm happy to help!"
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
            'help':             self._handle_help,
            'general':          self._handle_general,
        }
        return handlers.get(intent, self._handle_general)(message, entities, sentiment)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _format_property(self, prop, include_link=True):
        """Format a property card using [icon] markers for Lucide rendering"""
        ptype = 'For Sale' if prop.property_type == 'FOR_SALE' else 'For Rent'
        lines = [
            f"[home] {prop.title}",
            f"  [dollar-sign] ${prop.price:,.0f} ({ptype})",
            f"  [bed] {prop.beds} bed  [droplets] {prop.baths} bath  [maximize] {prop.sqft:,} sqft",
            f"  [map-pin] {prop.city}, {prop.state}",
        ]
        if include_link:
            lines.append(f"  [external-link] /properties/{prop.slug}")
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
            "Hello! Welcome to Lily White Realestate. How can I help you find your perfect property today?",
            "Hi there! I'm your real estate assistant. Looking to buy, rent, or sell? Just ask!",
            "Welcome! I can help you explore our properties, connect with agents, or answer any real estate questions.",
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
        msg_lower = message.lower()
        for prop in Property.objects.filter(status='AVAILABLE'):
            if prop.title.lower() in msg_lower or prop.slug.replace('-', ' ') in msg_lower:
                ptype = 'For Sale' if prop.property_type == 'FOR_SALE' else 'For Rent'
                amenities = ', '.join(prop.amenities_list[:5]) if prop.amenities_list else 'N/A'
                lines = [
                    f"[home] {prop.title}",
                    f"[dollar-sign] ${prop.price:,.0f} ({ptype})",
                    f"[map-pin] {prop.address}, {prop.city}, {prop.state} {prop.zip_code}",
                    f"[bed] {prop.beds} bed  [droplets] {prop.baths} bath  [car] {prop.garage} garage",
                    f"[maximize] {prop.sqft:,} sqft" + (f"  [trees] {prop.lot_size:,} sqft lot" if prop.lot_size else ""),
                ]
                if prop.year_built:
                    lines.append(f"[calendar] Year built: {prop.year_built}")
                lines.append(f"[star] Features: {amenities}")
                lines.append(f"[external-link] /properties/{prop.slug}")
                return "\n".join(lines)

        return (
            "I'd be happy to give you details on any property!\n"
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
                f"No properties found under ${budget:,}.\n"
                f"[dollar-sign] Our most affordable listing starts at ${min_price:,.0f}. Would you like to see it?"
            )

        props = Property.objects.filter(status='AVAILABLE').order_by('price')
        if props.exists():
            return (
                f"[dollar-sign] Our properties range from ${props.first().price:,.0f} to ${props.last().price:,.0f}.\n\n"
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
                f"[map-pin] We have properties in: {', '.join(cities)}.\n\n"
                "Which area interests you? I can show you what's available there."
            )
        return "Tell me which city or neighborhood you're interested in!"

    def _handle_schedule_viewing(self, message, entities, sentiment):
        try:
            agent = Agent.objects.filter(is_active=True).first()
            if agent:
                return (
                    "I'd love to arrange a viewing for you! Contact our agent directly:\n\n"
                    f"[user] {agent.name}\n"
                    f"[phone] {agent.phone}\n"
                    f"[mail] {agent.email}\n\n"
                    "Or fill out the contact form on any property page and we'll schedule a tour within 24 hours."
                )
        except Exception:
            pass
        return (
            "To schedule a viewing, please contact us:\n\n"
            "[phone] (555) 123-4567\n"
            "[mail] info@realtorpal.com\n\n"
            "We'll arrange a convenient time within 24 hours!"
        )

    def _handle_contact(self, message, entities, sentiment):
        try:
            agents = Agent.objects.filter(is_active=True)
            if agents.exists():
                response = "Our agents are ready to help you:\n\n"
                for agent in agents:
                    response += (
                        f"[user] {agent.name}\n"
                        f"[phone] {agent.phone}\n"
                        f"[mail] {agent.email}\n\n"
                    )
                response += "[clock] Available Monday-Friday, 9 AM - 6 PM."
                return response
        except Exception:
            pass
        return (
            "[phone] (555) 123-4567\n"
            "[mail] info@realtorpal.com\n\n"
            "[clock] Available Monday-Friday, 9 AM - 6 PM."
        )

    def _handle_sell_property(self, message, entities, sentiment):
        return (
            "Thinking of selling? Great choice! Here's how we help:\n\n"
            "[check-circle] Free property valuation\n"
            "[check-circle] Professional photography and listing\n"
            "[check-circle] Marketing across all major platforms\n"
            "[check-circle] Expert negotiation to get you the best price\n"
            "[check-circle] Full paperwork support\n\n"
            "Would you like to schedule a free consultation with one of our agents?"
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
            "We can connect you with trusted mortgage advisors who can help you:\n\n"
            "[check-circle] Get pre-approved quickly\n"
            "[check-circle] Compare rates from multiple lenders\n"
            "[check-circle] Calculate your monthly payments\n"
            "[check-circle] Understand all your financing options\n\n"
            "Would you like us to arrange a free consultation with a mortgage specialist?"
        )

    def _handle_help(self, message, entities, sentiment):
        try:
            faqs = FAQ.objects.filter(is_active=True).order_by('order')
            if faqs.exists():
                # Group by category
                categories: dict = {}
                for faq in faqs:
                    categories.setdefault(faq.category, []).append(faq)

                response = "Here are our frequently asked questions:\n\n"
                for category, items in categories.items():
                    response += f"[tag] {category}\n"
                    for faq in items:
                        response += f"[help-circle] {faq.question}\n"
                    response += "\n"
                response += "Ask me any of these questions and I'll give you the full answer!"
                return response
        except Exception:
            pass
        return (
            "I can help you with:\n\n"
            "[home] Finding properties for sale or rent\n"
            "[dollar-sign] Budget and pricing questions\n"
            "[map-pin] Properties by location\n"
            "[calendar] Scheduling viewings\n"
            "[user] Connecting with our agents\n"
            "[tag] Selling your property\n"
            "[credit-card] Mortgage and financing\n\n"
            "What would you like to know?"
        )

    def _handle_general(self, message, entities, sentiment):
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['all properties', 'all listings', 'everything', 'show me all']):
            return self._handle_property_search(message, entities, sentiment)

        if sentiment.get('compound', 0) < -0.5:
            return (
                "I'm sorry to hear that - I'm here to help! "
                "Could you tell me more about what you're looking for? "
                "I'll do my best to find the right property for you."
            )

        total = Property.objects.filter(status='AVAILABLE').count()
        return (
            f"I'm your Lily White Realestate assistant! We currently have {total} available properties.\n\n"
            "You can ask me things like:\n"
            "[search] Show me 3-bedroom homes under $300,000\n"
            "[map-pin] What properties are available in Los Angeles?\n"
            "[info] Tell me about the Beachfront Paradise\n"
            "[home] I want to rent a condo\n\n"
            "What are you looking for?"
        )
