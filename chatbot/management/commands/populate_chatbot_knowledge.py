"""
Management command to populate chatbot knowledge base with all responses.
This removes hardcoded responses and makes everything customizable from Django admin.

Usage:
    python manage.py populate_chatbot_knowledge
    python manage.py populate_chatbot_knowledge --clear  # Clear existing first
"""

from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotRule


class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with all responses (removes hardcoded data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing knowledge base before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing knowledge base...')
            KnowledgeBase.objects.all().delete()
            ChatbotRule.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing data'))

        self.stdout.write('Populating chatbot knowledge base...')

        # ============================================================
        # GREETINGS & GOODBYES
        # ============================================================
        greetings = [
            {
                'question': 'hello',
                'answer': "Hello! 👋 Welcome to Lily White Real Estate!\n\nI'm your AI assistant, here to help you find your dream property. With 12+ years of experience and $85M+ saved for our clients, we're committed to making your property journey smooth and successful.\n\nHow can I assist you today?",
                'category': 'greeting',
                'keywords': 'hello, hi, hey, greetings, good morning, good afternoon, good evening',
                'priority': 10
            },
            {
                'question': 'goodbye',
                'answer': "Thank you for chatting with me! 👋\n\nIf you need anything else, I'm always here to help. Have a wonderful day!\n\nFor immediate assistance, contact us:\nPhone: +600414701721\nEmail: Bijen@lilywhiterealestate.com.au",
                'category': 'goodbye',
                'keywords': 'bye, goodbye, see you, thanks, thank you, exit, quit',
                'priority': 10
            }
        ]

        # ============================================================
        # CONTACT INFORMATION
        # ============================================================
        contact_info = [
            {
                'question': 'contact information',
                'answer': "CONTACT LILY WHITE REAL ESTATE\n\nWe'd love to hear from you! Here's how to reach us:\n\n📞 Phone: +600414701721\n📧 Email: Bijen@lilywhiterealestate.com.au\n🌐 Website: www.lilywhiterealestate.com.au\n\n🏢 Office Hours:\nMonday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: By appointment\n\nOur team typically responds within 1 business hour during office hours.",
                'category': 'contact',
                'keywords': 'contact, phone, email, reach, call, message, office hours, location, address',
                'priority': 9
            },
            {
                'question': 'agent information',
                'answer': "MEET OUR PRINCIPAL AGENT\n\n👤 Bijen - Principal Agent\n📞 Phone: +600414701721\n📧 Email: Bijen@lilywhiterealestate.com.au\n\n🏆 Experience: 12+ years in real estate\n💰 Client Savings: $85M+ saved for clients\n📍 Coverage: 24 locations across the region\n\nBijen specializes in:\n- Residential property sales\n- Investment property guidance\n- First home buyer assistance\n- Property portfolio management\n- Market analysis and insights\n\nSchedule a consultation today!",
                'category': 'agent',
                'keywords': 'agent, bijen, principal, who are you, meet agent, real estate agent, contact agent',
                'priority': 9
            }
        ]

        # ============================================================
        # SERVICES
        # ============================================================
        services = [
            {
                'question': 'what services do you offer',
                'answer': "OUR COMPREHENSIVE REAL ESTATE SERVICES\n\n🏠 BUYING SERVICES\n- Property search and selection\n- Market analysis and insights\n- Negotiation and offer preparation\n- First home buyer guidance\n- Investment property analysis\n\n💼 SELLING SERVICES\n- Property valuation and pricing strategy\n- Professional marketing and photography\n- Open home coordination\n- Negotiation with buyers\n- Settlement assistance\n\n💰 FINANCIAL SERVICES\n- Home loan assistance\n- Mortgage broker connections\n- Investment loan strategies\n- Pre-approval guidance\n\n📊 INVESTMENT SERVICES\n- Portfolio diversification\n- Rental yield optimization\n- Tax-effective structures\n- Long-term wealth building\n\n🎯 WHY CHOOSE US?\n- 12+ years of experience\n- $85M+ saved for clients\n- 24 locations covered\n- Personalized service\n\nWhat service interests you most?",
                'category': 'services',
                'keywords': 'services, what do you do, help with, offer, provide, assistance, buying, selling',
                'priority': 9
            },
            {
                'question': 'buying process',
                'answer': "YOUR HOME BUYING JOURNEY\n\nWe make buying property simple and stress-free:\n\n1️⃣ CONSULTATION\n- Discuss your needs and budget\n- Understand your preferences\n- Set realistic expectations\n\n2️⃣ PROPERTY SEARCH\n- Access to exclusive listings\n- Personalized property matches\n- Market insights and analysis\n\n3️⃣ PROPERTY VIEWING\n- Schedule convenient tours\n- Expert property evaluation\n- Neighborhood insights\n\n4️⃣ OFFER & NEGOTIATION\n- Strategic offer preparation\n- Professional negotiation\n- Contract review assistance\n\n5️⃣ FINANCE & SETTLEMENT\n- Home loan assistance\n- Settlement coordination\n- Final inspections\n\n6️⃣ HANDOVER\n- Key collection\n- Move-in support\n- After-sales service\n\nReady to start your journey? Let's find your dream home!",
                'category': 'buying',
                'keywords': 'buying process, how to buy, purchase property, buying steps, home buying',
                'priority': 8
            },
            {
                'question': 'selling process',
                'answer': "SELLING YOUR PROPERTY WITH US\n\nMaximize your property's value with our proven process:\n\n1️⃣ PROPERTY APPRAISAL\n- Free market valuation\n- Comparative market analysis\n- Pricing strategy discussion\n\n2️⃣ MARKETING PREPARATION\n- Professional photography\n- Property styling advice\n- Marketing material creation\n\n3️⃣ LISTING & PROMOTION\n- Multi-platform advertising\n- Social media campaigns\n- Email marketing to buyers\n\n4️⃣ OPEN HOMES & VIEWINGS\n- Scheduled open inspections\n- Private viewings\n- Buyer feedback collection\n\n5️⃣ OFFERS & NEGOTIATION\n- Review all offers\n- Strategic negotiation\n- Best price achievement\n\n6️⃣ SETTLEMENT\n- Contract management\n- Settlement coordination\n- Smooth handover\n\n💰 AVERAGE RESULTS:\n- 95% of asking price achieved\n- 30-45 days average sale time\n- $85M+ saved for clients\n\nReady to sell? Contact us for a free appraisal!",
                'category': 'selling',
                'keywords': 'selling process, how to sell, sell property, selling steps, list property',
                'priority': 8
            }
        ]

        # ============================================================
        # MORTGAGE & INVESTMENT
        # ============================================================
        financial = [
            {
                'question': 'home loan assistance',
                'answer': "HOME LOAN ASSISTANCE\n\nNavigating home loans can be complex. We're here to help!\n\n💰 OUR LOAN SERVICES:\n- Home loan comparison and selection\n- Connecting with trusted lenders\n- Pre-approval assistance\n- Investment loan strategies\n- Refinancing guidance\n- First home buyer grants\n\n🎯 BENEFITS:\n- Access to multiple lenders\n- Competitive interest rates\n- Fast pre-approval process\n- Expert advice and support\n\n📋 WHAT YOU'LL NEED:\n- Proof of income\n- Employment details\n- Asset and liability information\n- Identification documents\n\nFor detailed home loan assistance, contact Bijen:\n\n📞 Phone: +600414701721\n📧 Email: Bijen@lilywhiterealestate.com.au\n\nLet's get you pre-approved today!",
                'category': 'mortgage',
                'keywords': 'home loan, mortgage, finance, loan, pre-approval, lender, interest rate, refinance',
                'priority': 8
            },
            {
                'question': 'investment property guidance',
                'answer': "INVESTMENT PROPERTY GUIDANCE\n\nBuilding a property investment portfolio? You're in the right place!\n\n📊 WITH 12+ YEARS OF EXPERIENCE AND $85M+ SAVED FOR CLIENTS, WE CAN HELP YOU WITH:\n\n🏢 INVESTMENT SERVICES:\n- Investment property selection and analysis\n- Portfolio diversification strategies\n- Rental yield optimization\n- Tax-effective investment structures\n- Long-term wealth building through property\n- Market insights across 24 locations\n\n💡 INVESTMENT STRATEGIES:\n- Capital growth properties\n- High rental yield properties\n- Renovation opportunities\n- Off-the-plan investments\n- Commercial property options\n\n📈 WHY INVEST WITH US?\n- Data-driven property analysis\n- Market trend insights\n- Rental return projections\n- Tax benefit guidance\n- Long-term wealth planning\n\nLet's discuss your investment goals:\n\n📞 Phone: +600414701721\n📧 Email: Bijen@lilywhiterealestate.com.au",
                'category': 'investment',
                'keywords': 'investment, invest, portfolio, rental, yield, capital growth, investor, property investment',
                'priority': 8
            }
        ]

        # ============================================================
        # HELP & GENERAL
        # ============================================================
        help_general = [
            {
                'question': 'how can you help me',
                'answer': "HOW I CAN HELP YOU\n\nI'm here to assist you with all your property needs!\n\n🏠 PROPERTY SEARCH:\n- Search by bedrooms, price, location\n- View property details and photos\n- Schedule property viewings\n- Get market insights\n\n💼 SERVICES:\n- Buying properties (residential or investment)\n- Selling your property for the best price\n- Finding rental properties\n- Investment portfolio guidance\n- Home loan assistance\n\n📞 CONTACT & SUPPORT:\n- Connect with our agents\n- Schedule consultations\n- Get property valuations\n- Ask questions anytime\n\n❓ COMMON QUESTIONS:\n- Property search tips\n- Buying/selling process\n- Market conditions\n- Financing options\n\nWhat would you like to know more about?",
                'category': 'help',
                'keywords': 'help, assist, support, what can you do, how to use, guide, tutorial',
                'priority': 7
            },
            {
                'question': 'about lily white real estate',
                'answer': "ABOUT LILY WHITE REAL ESTATE\n\n🏆 WHO WE ARE:\nLily White Real Estate is a trusted name in property services with a proven track record of excellence.\n\n📊 OUR ACHIEVEMENTS:\n- 12+ years of industry experience\n- $85M+ saved for our clients\n- 24 locations covered\n- Hundreds of satisfied clients\n- Award-winning service\n\n💡 OUR MISSION:\nTo provide exceptional real estate services that exceed expectations and build lasting relationships with our clients.\n\n🎯 WHY CHOOSE US?\n- Personalized service tailored to your needs\n- Expert market knowledge and insights\n- Professional negotiation skills\n- Comprehensive property services\n- Transparent and honest communication\n- After-sales support and guidance\n\n👥 OUR TEAM:\nLed by Principal Agent Bijen, our experienced team is dedicated to helping you achieve your property goals.\n\n📞 GET IN TOUCH:\nPhone: +600414701721\nEmail: Bijen@lilywhiterealestate.com.au\n\nLet's make your property dreams a reality!",
                'category': 'about',
                'keywords': 'about, who are you, company, lily white, real estate, experience, team',
                'priority': 7
            }
        ]

        # ============================================================
        # COMBINE ALL KNOWLEDGE
        # ============================================================
        all_knowledge = (
            greetings + contact_info + services + 
            financial + help_general
        )

        # Create KnowledgeBase entries
        created_count = 0
        for item in all_knowledge:
            kb, created = KnowledgeBase.objects.get_or_create(
                question=item['question'],
                defaults={
                    'answer': item['answer'],
                    'category': item['category'],
                    'keywords': item['keywords'],
                    'priority': item['priority'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {item['question']}")
            else:
                self.stdout.write(f"  - Exists: {item['question']}")

        # ============================================================
        # SUMMARY
        # ============================================================
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully populated chatbot knowledge base!'))
        self.stdout.write(f'  - Knowledge entries: {created_count} created')
        self.stdout.write(f'  - Total knowledge: {KnowledgeBase.objects.count()} entries')
        self.stdout.write('='*60)
        self.stdout.write('\n📝 Next steps:')
        self.stdout.write('  1. Visit http://localhost:8000/admin/chatbot/knowledgebase/')
        self.stdout.write('  2. Customize responses as needed')
        self.stdout.write('  3. Add more Q&A pairs')
        self.stdout.write('  4. Test chatbot with new responses')
        self.stdout.write('\n💡 Note: Chatbot Rules are optional for advanced pattern matching.')
        self.stdout.write('   The Knowledge Base semantic search will handle most queries.')
        self.stdout.write('\n✨ All chatbot responses are now customizable from Django admin!')
