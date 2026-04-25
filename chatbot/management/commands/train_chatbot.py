"""
Management command to train the chatbot with comprehensive website knowledge.
Usage: python manage.py train_chatbot
"""

from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase, ChatbotRule


class Command(BaseCommand):
    help = 'Train chatbot with comprehensive website knowledge'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Training chatbot with website knowledge...'))

        # Clear existing knowledge (optional - comment out to keep existing)
        # KnowledgeBase.objects.all().delete()
        # ChatbotRule.objects.all().delete()

        # ============================================================
        # CHATBOT RULES (Highest Priority - Exact Matches)
        # ============================================================
        rules = [
            {
                'name': 'Greeting - Hello',
                'pattern': r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
                'match_type': 'regex',
                'response': (
                    "Hello! Welcome to Lily White Real Estate.\n\n"
                    "I can help you with:\n"
                    "- Finding properties for sale or rent\n"
                    "- Pricing and budget guidance\n"
                    "- Connecting with our agents\n"
                    "- Scheduling property viewings\n\n"
                    "What are you looking for today?"
                ),
                'priority': 100,
            },
            {
                'name': 'Home Worth Inquiry',
                'pattern': r'(home worth|property worth|house value|what.*worth|valuation)',
                'match_type': 'regex',
                'response': (
                    "PROPERTY VALUATION\n\n"
                    "We offer FREE property valuations. Our expert team will:\n"
                    "- Analyze current market trends\n"
                    "- Compare with recent sales\n"
                    "- Provide accurate valuation\n\n"
                    "Visit our 'What's My Home Worth?' page or contact us:\n\n"
                    "Phone: +600414701721\n"
                    "Email: Bijen@lilywhiterealestate.com.au"
                ),
                'priority': 95,
            },
            {
                'name': 'Contact Information',
                'pattern': r'(contact|phone|email|reach|call|message)',
                'match_type': 'regex',
                'response': (
                    "CONTACT INFORMATION\n\n"
                    "Phone: +600414701721\n"
                    "Email: Bijen@lilywhiterealestate.com.au\n\n"
                    "Business Hours:\n"
                    "Monday - Friday: 9:00 AM - 6:00 PM\n"
                    "Saturday: 10:00 AM - 4:00 PM\n"
                    "Sunday: By Appointment\n\n"
                    "You can also fill out our contact form on the website."
                ),
                'priority': 90,
            },
        ]

        for rule_data in rules:
            rule, created = ChatbotRule.objects.update_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            status = '✅ Created' if created else '🔄 Updated'
            self.stdout.write(f"{status} Rule: {rule.name}")

        # ============================================================
        # KNOWLEDGE BASE - SERVICES
        # ============================================================
        services_kb = [
            {
                'question': 'What services do you offer?',
                'answer': (
                    "OUR SERVICES\n\n"
                    "BUYING PROPERTIES\n"
                    "- Residential homes\n"
                    "- Investment properties\n"
                    "- First-time buyer assistance\n\n"
                    "SELLING PROPERTIES\n"
                    "- Free market appraisal\n"
                    "- Professional marketing\n"
                    "- Negotiation expertise\n\n"
                    "RENTAL SERVICES\n"
                    "- Property management\n"
                    "- Tenant screening\n"
                    "- Lease agreements\n\n"
                    "INVESTMENT GUIDANCE\n"
                    "- Portfolio building\n"
                    "- ROI analysis\n"
                    "- Market insights\n\n"
                    "HOME LOAN ASSISTANCE\n"
                    "- Mortgage pre-approval\n"
                    "- Lender connections\n"
                    "- Finance options"
                ),
                'keywords': 'services, offer, provide, help, do',
                'category': 'services',
                'priority': 80,
            },
            {
                'question': 'How can you help me buy a property?',
                'answer': (
                    "BUYING PROCESS\n\n"
                    "STEP 1: Understanding Your Needs\n"
                    "- Budget assessment\n"
                    "- Location preferences\n"
                    "- Property requirements\n\n"
                    "STEP 2: Property Search\n"
                    "- Curated listings matching your criteria\n"
                    "- Market insights and trends\n"
                    "- Neighborhood information\n\n"
                    "STEP 3: Viewings & Inspections\n"
                    "- Schedule property tours\n"
                    "- Professional inspection coordination\n\n"
                    "STEP 4: Offer & Negotiation\n"
                    "- Competitive offer strategy\n"
                    "- Expert negotiation\n\n"
                    "STEP 5: Closing\n"
                    "- Contract review\n"
                    "- Settlement coordination\n\n"
                    "Let's start! What's your budget and preferred location?"
                ),
                'keywords': 'buy, buying, purchase, buyer',
                'category': 'buying',
                'priority': 75,
            },
            {
                'question': 'How do you help with selling my property?',
                'answer': (
                    "SELLING SERVICES\n\n"
                    "FREE MARKET APPRAISAL\n"
                    "- Accurate pricing strategy\n"
                    "- Comparative market analysis\n\n"
                    "PROFESSIONAL MARKETING\n"
                    "- High-quality photography\n"
                    "- Virtual tours\n"
                    "- Online and offline advertising\n\n"
                    "BUYER SCREENING\n"
                    "- Qualified buyer identification\n"
                    "- Pre-approved buyers priority\n\n"
                    "EXPERT NEGOTIATION\n"
                    "- Best price achievement\n"
                    "- Terms optimization\n\n"
                    "SETTLEMENT SUPPORT\n"
                    "- Legal coordination\n"
                    "- Smooth transaction\n\n"
                    "Ready to sell? Contact us for a FREE valuation."
                ),
                'keywords': 'sell, selling, seller, list, listing',
                'category': 'selling',
                'priority': 75,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - ABOUT / AGENT PROFILE
        # ============================================================
        about_kb = [
            {
                'question': 'Who is the agent?',
                'answer': (
                    "MEET BIJEN KHADKA\n"
                    "Investment Property Specialist\n\n"
                    "Experience: 12+ years in real estate\n"
                    "Clients Served: 1500+ satisfied clients\n"
                    "Specialization: Investment properties and residential sales\n\n"
                    "WHY CHOOSE ME:\n"
                    "- Deep market knowledge\n"
                    "- Proven track record\n"
                    "- Personalized service\n"
                    "- Strong negotiation skills\n"
                    "- Extensive network\n\n"
                    "I'm committed to helping you achieve your real estate goals."
                ),
                'keywords': 'agent, who, about, bijen, khadka, experience',
                'category': 'about',
                'priority': 70,
            },
            {
                'question': 'What is your experience?',
                'answer': (
                    "EXPERIENCE & EXPERTISE\n\n"
                    "With 12+ years in real estate, I have:\n"
                    "- Helped 1500+ clients buy, sell, and invest\n"
                    "- Closed millions in property transactions\n"
                    "- Built a reputation for excellence\n"
                    "- Developed deep market expertise\n"
                    "- Created lasting client relationships\n\n"
                    "My experience means you get:\n"
                    "- Market insights\n"
                    "- Negotiation expertise\n"
                    "- Smooth transactions\n"
                    "- Trusted guidance"
                ),
                'keywords': 'experience, years, expertise, track record',
                'category': 'about',
                'priority': 65,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - PROPERTIES
        # ============================================================
        properties_kb = [
            {
                'question': 'What properties do you have available?',
                'answer': (
                    "AVAILABLE PROPERTIES\n\n"
                    "FOR SALE:\n"
                    "- Single-family homes\n"
                    "- Condos and apartments\n"
                    "- Townhouses\n"
                    "- Investment properties\n"
                    "- Luxury estates\n\n"
                    "FOR RENT:\n"
                    "- Residential rentals\n"
                    "- Commercial spaces\n"
                    "- Short-term and long-term\n\n"
                    "To see current listings, tell me:\n"
                    "1. Your budget range\n"
                    "2. Preferred location\n"
                    "3. Property type\n"
                    "4. Number of bedrooms/bathrooms\n\n"
                    "Or visit our Properties page to browse all listings."
                ),
                'keywords': 'properties, available, listings, houses, homes',
                'category': 'properties',
                'priority': 75,
            },
            {
                'question': 'How do I search for properties?',
                'answer': (
                    "PROPERTY SEARCH OPTIONS\n\n"
                    "OPTION 1: Tell Me Your Requirements\n"
                    "Just share:\n"
                    "- Budget (e.g., under $500k)\n"
                    "- Location (e.g., downtown or near schools)\n"
                    "- Bedrooms (e.g., 3 bedroom)\n"
                    "- Property type (e.g., house or condo)\n\n"
                    "OPTION 2: Browse Our Website\n"
                    "Visit the Properties page to:\n"
                    "- Filter by price, location, size\n"
                    "- View photos and details\n"
                    "- Save favorites\n"
                    "- Schedule viewings\n\n"
                    "What are you looking for?"
                ),
                'keywords': 'search, find, looking for, browse',
                'category': 'properties',
                'priority': 70,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - PROCESS & HOW IT WORKS
        # ============================================================
        process_kb = [
            {
                'question': 'How does the buying process work?',
                'answer': (
                    "HOME BUYING PROCESS\n\n"
                    "STEP 1: Pre-Approval (1-3 days)\n"
                    "- Get mortgage pre-approval\n"
                    "- Know your budget\n\n"
                    "STEP 2: Property Search (2-8 weeks)\n"
                    "- Browse listings\n"
                    "- Schedule viewings\n"
                    "- Compare options\n\n"
                    "STEP 3: Make an Offer (1-3 days)\n"
                    "- Submit competitive offer\n"
                    "- Negotiate terms\n\n"
                    "STEP 4: Inspection (1-2 weeks)\n"
                    "- Professional property inspection\n"
                    "- Review findings\n\n"
                    "STEP 5: Financing (2-4 weeks)\n"
                    "- Finalize mortgage\n"
                    "- Appraisal completed\n\n"
                    "STEP 6: Closing (1-2 weeks)\n"
                    "- Sign documents\n"
                    "- Transfer ownership\n"
                    "- Receive keys\n\n"
                    "Total Timeline: 6-12 weeks"
                ),
                'keywords': 'process, how, steps, timeline, buying process',
                'category': 'process',
                'priority': 70,
            },
            {
                'question': 'How long does it take to sell a house?',
                'answer': (
                    "SELLING TIMELINE\n\n"
                    "WEEK 1-2: Preparation\n"
                    "- Market appraisal\n"
                    "- Property staging\n"
                    "- Professional photos\n\n"
                    "WEEK 2-3: Marketing Launch\n"
                    "- List property\n"
                    "- Online advertising\n"
                    "- Open houses\n\n"
                    "WEEK 3-8: Showings and Offers\n"
                    "- Buyer viewings\n"
                    "- Receive offers\n"
                    "- Negotiate terms\n\n"
                    "WEEK 8-12: Closing\n"
                    "- Buyer inspection\n"
                    "- Financing approval\n"
                    "- Settlement\n\n"
                    "Average: 8-12 weeks\n\n"
                    "Factors affecting timeline:\n"
                    "- Market conditions\n"
                    "- Property condition\n"
                    "- Pricing strategy\n"
                    "- Location demand"
                ),
                'keywords': 'how long, timeline, sell, selling time',
                'category': 'process',
                'priority': 65,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - PRICING & FINANCING
        # ============================================================
        pricing_kb = [
            {
                'question': 'What are your fees and commissions?',
                'answer': (
                    "FEE STRUCTURE\n\n"
                    "FOR SELLERS:\n"
                    "- Commission: Competitive market rates\n"
                    "- FREE market appraisal\n"
                    "- FREE professional photography\n"
                    "- No upfront costs\n\n"
                    "FOR BUYERS:\n"
                    "- Buyer representation: Often covered by seller\n"
                    "- No hidden fees\n"
                    "- Transparent pricing\n\n"
                    "ADDITIONAL SERVICES:\n"
                    "- Property management: Custom packages\n"
                    "- Investment consulting: By arrangement\n\n"
                    "For specific pricing details, please contact:\n"
                    "Phone: +600414701721\n"
                    "Email: Bijen@lilywhiterealestate.com.au\n\n"
                    "I'll provide a detailed breakdown for your situation."
                ),
                'keywords': 'fees, commission, cost, price, charges',
                'category': 'pricing',
                'priority': 75,
            },
            {
                'question': 'Can you help with financing?',
                'answer': (
                    "HOME LOAN ASSISTANCE\n\n"
                    "MORTGAGE PRE-APPROVAL\n"
                    "- Connect with trusted lenders\n"
                    "- Get pre-approved quickly\n"
                    "- Strengthen your offer\n\n"
                    "FINANCE OPTIONS\n"
                    "- Compare loan products\n"
                    "- Fixed vs variable rates\n"
                    "- First-time buyer programs\n\n"
                    "LENDER NETWORK\n"
                    "- Multiple lender access\n"
                    "- Competitive rates\n"
                    "- Expert guidance\n\n"
                    "SUPPORT THROUGHOUT\n"
                    "- Application assistance\n"
                    "- Document preparation\n"
                    "- Closing coordination\n\n"
                    "Ready to explore financing? Let's discuss your situation."
                ),
                'keywords': 'financing, loan, mortgage, finance, lending',
                'category': 'financing',
                'priority': 70,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - TESTIMONIALS & TRUST
        # ============================================================
        testimonials_kb = [
            {
                'question': 'Do you have client testimonials?',
                'answer': (
                    "CLIENT TESTIMONIALS\n\n"
                    "1500+ Satisfied Clients\n"
                    "12+ Years of Excellence\n"
                    "Countless Success Stories\n\n"
                    "WHAT CLIENTS SAY:\n"
                    "- \"Professional and knowledgeable\"\n"
                    "- \"Made the process stress-free\"\n"
                    "- \"Got us the best price\"\n"
                    "- \"Highly recommend\"\n"
                    "- \"Excellent communication\"\n\n"
                    "Visit our Testimonials page to read detailed reviews from:\n"
                    "- First-time buyers\n"
                    "- Sellers\n"
                    "- Investors\n"
                    "- Renters\n\n"
                    "Your success is my priority."
                ),
                'keywords': 'testimonials, reviews, clients, feedback, success',
                'category': 'general',
                'priority': 60,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - FAQS
        # ============================================================
        faqs_kb = [
            {
                'question': 'What areas do you serve?',
                'answer': (
                    "SERVICE AREAS\n\n"
                    "PRIMARY MARKETS:\n"
                    "- Main cities and neighborhoods\n"
                    "- Metropolitan areas\n"
                    "- Suburban communities\n\n"
                    "EXTENDED SERVICE AREA:\n"
                    "- Regional coverage\n"
                    "- County-wide service\n\n"
                    "Not sure if I cover your area? Just ask.\n"
                    "I have a strong network and can help you anywhere."
                ),
                'keywords': 'areas, location, serve, where, coverage',
                'category': 'general',
                'priority': 65,
            },
            {
                'question': 'How do I schedule a viewing?',
                'answer': (
                    "SCHEDULE A VIEWING\n\n"
                    "OPTION 1: Tell Me Now\n"
                    "Just say: \"I want to view [property address]\"\n"
                    "I'll arrange it for you.\n\n"
                    "OPTION 2: Contact Directly\n"
                    "Phone: +600414701721\n"
                    "Email: Bijen@lilywhiterealestate.com.au\n\n"
                    "OPTION 3: Website\n"
                    "Click \"Schedule Viewing\" on any property listing\n\n"
                    "WHAT I NEED:\n"
                    "- Property address or listing ID\n"
                    "- Your preferred date/time\n"
                    "- Contact information\n\n"
                    "I'll confirm within 24 hours."
                ),
                'keywords': 'viewing, schedule, appointment, visit, tour',
                'category': 'general',
                'priority': 70,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - BLOG & RESOURCES
        # ============================================================
        blog_kb = [
            {
                'question': 'Do you have a blog or resources?',
                'answer': (
                    "BLOG & RESOURCES\n\n"
                    "TOPICS COVERED:\n"
                    "- Market trends and analysis\n"
                    "- Buying and selling tips\n"
                    "- Investment strategies\n"
                    "- Neighborhood guides\n"
                    "- Home maintenance advice\n"
                    "- Real estate news\n\n"
                    "LATEST ARTICLES:\n"
                    "Check our Blog page for the most recent posts.\n\n"
                    "STAY UPDATED:\n"
                    "Subscribe to our newsletter for:\n"
                    "- New listings\n"
                    "- Market updates\n"
                    "- Expert tips\n"
                    "- Exclusive opportunities"
                ),
                'keywords': 'blog, articles, resources, tips, guides',
                'category': 'general',
                'priority': 55,
            },
        ]

        # ============================================================
        # KNOWLEDGE BASE - PROJECTS & PORTFOLIO
        # ============================================================
        projects_kb = [
            {
                'question': 'What projects have you completed?',
                'answer': (
                    "COMPLETED PROJECTS\n\n"
                    "RECENT ACHIEVEMENTS:\n"
                    "- Luxury home sales\n"
                    "- Investment property portfolios\n"
                    "- First-time buyer success stories\n"
                    "- Commercial property deals\n\n"
                    "VIEW OUR PROJECTS:\n"
                    "Visit the Projects page to see:\n"
                    "- Before and after transformations\n"
                    "- Success stories\n"
                    "- Property showcases\n"
                    "- Client testimonials\n\n"
                    "Each project represents my commitment to excellence."
                ),
                'keywords': 'projects, portfolio, completed, work, achievements',
                'category': 'general',
                'priority': 55,
            },
        ]

        # Combine all knowledge base entries
        all_kb = (
            services_kb + about_kb + properties_kb + process_kb + 
            pricing_kb + testimonials_kb + faqs_kb + blog_kb + projects_kb
        )

        # Create/Update Knowledge Base entries
        for kb_data in all_kb:
            kb, created = KnowledgeBase.objects.update_or_create(
                question=kb_data['question'],
                defaults=kb_data
            )
            status = '✅ Created' if created else '🔄 Updated'
            self.stdout.write(f"{status} KB: {kb.question[:50]}...")

        # ============================================================
        # SUMMARY
        # ============================================================
        total_rules = ChatbotRule.objects.filter(is_active=True).count()
        total_kb = KnowledgeBase.objects.filter(is_active=True).count()

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Chatbot Training Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f"📋 Active Rules: {total_rules}")
        self.stdout.write(f"📚 Knowledge Base Entries: {total_kb}")
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\n💡 The chatbot is now trained with:')
        self.stdout.write('   - Services information')
        self.stdout.write('   - Agent profile & experience')
        self.stdout.write('   - Property search guidance')
        self.stdout.write('   - Buying & selling processes')
        self.stdout.write('   - Pricing & financing help')
        self.stdout.write('   - Testimonials & trust signals')
        self.stdout.write('   - FAQs & common questions')
        self.stdout.write('   - Blog & resources')
        self.stdout.write('   - Projects & portfolio')
        self.stdout.write('\n🚀 Test the chatbot on your website!')
