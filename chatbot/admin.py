from django.contrib import admin
from django.utils.html import format_html
from .models import ChatSession, ChatMessage, KnowledgeBase, ChatbotRule


# ------------------------------------------------------------------ #
#  Chat Session & Message                                              #
# ------------------------------------------------------------------ #

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_label', 'user_name', 'user_email', 'user_phone', 'created_at', 'message_count']
    search_fields = ['session_id', 'user_name', 'user_email', 'user_phone']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']

    fieldsets = (
        ('Session', {'fields': ('session_id',)}),
        ('User Info (Optional)', {'fields': ('user_name', 'user_email', 'user_phone')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def session_label(self, obj):
        return obj.user_name or obj.user_email or obj.session_id[:12] + '...'
    session_label.short_description = 'Session'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'intent', 'confidence', 'created_at', 'message_preview']
    list_filter = ['intent', 'created_at']
    search_fields = ['message', 'response', 'session__session_id', 'session__user_name', 'session__user_email']
    readonly_fields = ['created_at', 'user_info_display']

    def user_info(self, obj):
        s = obj.session
        if s.user_name or s.user_email:
            return format_html(
                '<div style="font-size:11px;line-height:1.4;">'
                '<strong>{}</strong><br>'
                '<span style="color:#6c757d;">{}</span><br>'
                '<span style="color:#6c757d;">{}</span>'
                '</div>',
                s.user_name or 'Anonymous',
                s.user_email or '-',
                s.user_phone or '-',
            )
        return format_html('<span style="color:#999;">Anonymous</span>')
    user_info.short_description = 'User'

    def user_info_display(self, obj):
        s = obj.session
        return format_html(
            '<p style="margin:0;"><strong>Name:</strong> {}</p>'
            '<p style="margin:0;"><strong>Email:</strong> {}</p>'
            '<p style="margin:0;"><strong>Phone:</strong> {}</p>'
            '<p style="margin:0;"><strong>Session ID:</strong> <code>{}</code></p>',
            s.user_name or '-',
            s.user_email or '-',
            s.user_phone or '-',
            s.session_id,
        )
    user_info_display.short_description = 'User Information'

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

    fieldsets = (
        ('User Info', {'fields': ('user_info_display',)}),
        ('Session', {'fields': ('session',)}),
        ('Message', {'fields': ('message', 'response')}),
        ('Analysis', {'fields': ('intent', 'confidence')}),
        ('Metadata', {'fields': ('created_at',)}),
    )


# ------------------------------------------------------------------ #
#  Rule-Based Responses (Layer 0 — highest priority)                  #
# ------------------------------------------------------------------ #

@admin.register(ChatbotRule)
class ChatbotRuleAdmin(admin.ModelAdmin):
    """
    Rule-based chatbot responses — evaluated FIRST before everything else.
    Perfect for exact phrases, commands, greetings, and guaranteed answers.
    """
    list_display = (
        'name', 'match_type_badge', 'pattern_preview',
        'priority', 'is_active_icon', 'created_at'
    )
    list_filter = ('match_type', 'is_active', 'priority', 'created_at')
    search_fields = ('name', 'pattern', 'response')
    readonly_fields = ('created_at', 'updated_at', 'test_hint')
    list_editable = ('priority',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Rule Identity', {
            'fields': ('name', 'is_active', 'priority'),
            'description': 'Name is internal only. Priority: higher = evaluated first.',
        }),
        ('Pattern Matching', {
            'fields': ('match_type', 'pattern', 'test_hint'),
            'description': (
                'Define when this rule fires. '
                'Contains: fires if the user message includes the pattern. '
                'Exact: fires only if the message equals the pattern exactly. '
                'Regex: use Python regex for advanced matching.'
            ),
        }),
        ('Response', {
            'fields': ('response',),
            'description': (
                'Use [icon] markers: [home], [phone], [mail], [check-circle], '
                '[map-pin], [user], [clock], [dollar-sign], [calendar], etc.'
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def match_type_badge(self, obj):
        colors = {
            'exact':      '#6f42c1',
            'contains':   '#17a2b8',
            'startswith': '#28a745',
            'endswith':   '#fd7e14',
            'regex':      '#dc3545',
        }
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:3px;font-size:11px;">{}</span>',
            colors.get(obj.match_type, '#6c757d'),
            obj.get_match_type_display().split()[0],
        )
    match_type_badge.short_description = 'Match Type'
    match_type_badge.admin_order_field = 'match_type'

    def pattern_preview(self, obj):
        preview = obj.pattern[:80] + '...' if len(obj.pattern) > 80 else obj.pattern
        return format_html('<code style="color:#495057;font-size:12px;">{}</code>', preview)
    pattern_preview.short_description = 'Pattern'

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#28a745;font-size:18px;">✓</span>')
        return format_html('<span style="color:#dc3545;font-size:18px;">✗</span>')
    is_active_icon.short_description = 'Active'
    is_active_icon.admin_order_field = 'is_active'

    def test_hint(self, obj):
        labels = {
            'exact':      'equals exactly',
            'contains':   'contains',
            'startswith': 'starts with',
            'endswith':   'ends with',
            'regex':      'matches regex',
        }
        label = labels.get(obj.match_type, obj.match_type)
        return format_html(
            '<p style="color:#6c757d;font-size:12px;margin:0;">'
            'This rule fires when the user message <strong>{}</strong>: '
            '<code style="background:#f8f9fa;padding:2px 6px;border-radius:3px;">{}</code>'
            '</p>',
            label, obj.pattern,
        )
    test_hint.short_description = 'How this rule fires'

    actions = ['activate_rules', 'deactivate_rules']

    def activate_rules(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} rules activated.', 'success')
    activate_rules.short_description = '✓ Activate selected rules'

    def deactivate_rules(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} rules deactivated.', 'warning')
    deactivate_rules.short_description = '✗ Deactivate selected rules'


# ------------------------------------------------------------------ #
#  Knowledge Base (Layer 1 — keyword-matched Q&A)                     #
# ------------------------------------------------------------------ #

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """
    Admin for Knowledge Base — train the chatbot by adding Q&A pairs here.
    The chatbot automatically learns from this data without code changes.
    """
    list_display = (
        'question_preview', 'category_badge', 'priority',
        'is_active_icon', 'keyword_count', 'created_at'
    )
    list_filter = ('category', 'is_active', 'priority', 'created_at')
    search_fields = ('question', 'answer', 'keywords')
    readonly_fields = ('created_at', 'updated_at', 'keyword_preview')
    list_editable = ('priority',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Question & Answer', {
            'fields': ('question', 'answer'),
            'description': 'The question customers ask and the answer the chatbot will give.'
        }),
        ('Matching & Priority', {
            'fields': ('keywords', 'keyword_preview', 'category', 'priority'),
            'description': (
                'Keywords help the chatbot match customer questions. '
                'Leave blank to auto-detect from the question. '
                'Priority: higher numbers are checked first.'
            )
        }),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def question_preview(self, obj):
        preview = obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
        return format_html('<span style="font-weight:500;">{}</span>', preview)
    question_preview.short_description = 'Question'
    question_preview.admin_order_field = 'question'

    def category_badge(self, obj):
        return format_html(
            '<span style="background:#17a2b8;color:white;padding:3px 10px;border-radius:3px;font-size:11px;">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#28a745;font-size:18px;">✓</span>')
        return format_html('<span style="color:#dc3545;font-size:18px;">✗</span>')
    is_active_icon.short_description = 'Active'
    is_active_icon.admin_order_field = 'is_active'

    def keyword_count(self, obj):
        count = len(obj.keyword_list)
        return format_html('<span style="color:#007bff;">{} keywords</span>', count)
    keyword_count.short_description = 'Keywords'

    def keyword_preview(self, obj):
        keywords = obj.keyword_list[:10]
        preview = ', '.join(keywords)
        if len(obj.keyword_list) > 10:
            preview += f' ... (+{len(obj.keyword_list) - 10} more)'
        return format_html('<code style="color:#6c757d;font-size:12px;">{}</code>', preview)
    keyword_preview.short_description = 'Detected Keywords'

    actions = ['activate_entries', 'deactivate_entries', 'increase_priority', 'decrease_priority']

    def activate_entries(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} entries activated.', 'success')
    activate_entries.short_description = '✓ Activate selected entries'

    def deactivate_entries(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} entries deactivated.', 'warning')
    deactivate_entries.short_description = '✗ Deactivate selected entries'

    def increase_priority(self, request, queryset):
        for obj in queryset:
            obj.priority += 1
            obj.save()
        self.message_user(request, f'{queryset.count()} entries priority increased.', 'success')
    increase_priority.short_description = '↑ Increase priority'

    def decrease_priority(self, request, queryset):
        for obj in queryset:
            obj.priority = max(0, obj.priority - 1)
            obj.save()
        self.message_user(request, f'{queryset.count()} entries priority decreased.', 'info')
    decrease_priority.short_description = '↓ Decrease priority'
