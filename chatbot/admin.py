from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, get_object_or_404
from .models import ChatSession, ChatMessage, KnowledgeBase, ChatbotRule


# ------------------------------------------------------------------ #
#  Chat Session & Message                                              #
# ------------------------------------------------------------------ #

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_label', 'user_name', 'user_email', 'user_phone', 'created_at', 'message_count', 'view_chat_link']
    search_fields = ['session_id', 'user_name', 'user_email', 'user_phone']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']

    fieldsets = (
        ('Session', {'fields': ('session_id',)}),
        ('User Info', {'fields': ('user_name', 'user_email', 'user_phone')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:session_id>/chat/', self.admin_site.admin_view(self.chat_view), name='chatbot_chatsession_chat'),
        ]
        return custom + urls

    def chat_view(self, request, session_id):
        session = get_object_or_404(ChatSession, pk=session_id)
        messages = session.messages.order_by('created_at')
        context = {
            'session': session,
            'messages': messages,
            'title': f'Chat — {session.user_name or session.user_email or session.session_id[:12]}',
            'opts': ChatSession._meta,
            'app_label': 'chatbot',
            'available_apps': admin.site.get_app_list(request),
        }
        return render(request, 'admin/chatbot/chat_view.html', context)

    def session_label(self, obj):
        name = obj.user_name or obj.user_email or obj.session_id[:12] + '...'
        return format_html('<strong>{}</strong>', name)
    session_label.short_description = 'User'

    def message_count(self, obj):
        count = obj.messages.count()
        return format_html('<span style="background:#17a2b8;color:white;padding:2px 8px;border-radius:3px;font-size:11px;">{} msgs</span>', count)
    message_count.short_description = 'Messages'

    def view_chat_link(self, obj):
        return format_html(
            '<a href="{}/chat/" style="background:#c1a478;color:white;padding:3px 10px;border-radius:3px;font-size:11px;text-decoration:none;">View Chat</a>',
            obj.pk
        )
    view_chat_link.short_description = 'Chat'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'message_preview', 'response_preview', 'intent', 'created_at', 'view_session_link']
    list_filter = ['intent', 'created_at', 'session__user_name']
    search_fields = ['message', 'response', 'session__session_id', 'session__user_name', 'session__user_email']
    readonly_fields = ['created_at', 'user_info_display', 'full_conversation']

    def user_info(self, obj):
        s = obj.session
        name = s.user_name or s.user_email or 'Anonymous'
        color = '#c1a478' if s.user_name else '#6c757d'
        return format_html(
            '<div style="font-size:12px;">'
            '<strong style="color:{};">{}</strong>'
            '{}'
            '</div>',
            color, name,
            format_html('<br><span style="color:#aaa;font-size:11px;">{}</span>', s.user_email) if s.user_email else ''
        )
    user_info.short_description = 'User'

    def message_preview(self, obj):
        text = obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
        return format_html(
            '<div style="background:#f0f4f8;padding:4px 8px;border-radius:4px;font-size:12px;max-width:200px;">{}</div>',
            text
        )
    message_preview.short_description = 'User Message'

    def response_preview(self, obj):
        text = obj.response[:60] + '...' if len(obj.response) > 60 else obj.response
        return format_html(
            '<div style="background:#fff8f0;padding:4px 8px;border-radius:4px;font-size:12px;max-width:200px;border-left:3px solid #c1a478;">{}</div>',
            text
        )
    response_preview.short_description = 'Bot Response'

    def view_session_link(self, obj):
        return format_html(
            '<a href="/admin/chatbot/chatsession/{}/chat/" style="background:#5d6d87;color:white;padding:3px 10px;border-radius:3px;font-size:11px;text-decoration:none;">View Chat</a>',
            obj.session.pk
        )
    view_session_link.short_description = 'Chat'

    def user_info_display(self, obj):
        s = obj.session
        return format_html(
            '<p style="margin:0;"><strong>Name:</strong> {}</p>'
            '<p style="margin:0;"><strong>Email:</strong> {}</p>'
            '<p style="margin:0;"><strong>Phone:</strong> {}</p>'
            '<p style="margin:0;"><strong>Session ID:</strong> <code>{}</code></p>',
            s.user_name or '-', s.user_email or '-', s.user_phone or '-', s.session_id,
        )
    user_info_display.short_description = 'User Information'

    def full_conversation(self, obj):
        messages = obj.session.messages.order_by('created_at')
        html = ['<div style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;max-height:400px;overflow-y:auto;">']
        for m in messages:
            is_current = m.pk == obj.pk
            border = '3px solid #c1a478' if is_current else 'none'
            html.append(f'''
                <div style="padding:10px 14px;border-bottom:1px solid #f0f0f0;border-left:{border};">
                    <div style="font-size:11px;color:#aaa;margin-bottom:4px;">{m.created_at.strftime("%b %d, %H:%M")}</div>
                    <div style="background:#f0f4f8;padding:6px 10px;border-radius:6px;font-size:12px;margin-bottom:6px;"><strong>User:</strong> {m.message}</div>
                    <div style="background:#fff8f0;padding:6px 10px;border-radius:6px;font-size:12px;border-left:3px solid #c1a478;"><strong>Bot:</strong> {m.response[:200]}{"..." if len(m.response) > 200 else ""}</div>
                </div>
            ''')
        html.append('</div>')
        return format_html(''.join(html))
    full_conversation.short_description = 'Full Conversation'

    fieldsets = (
        ('User Info', {'fields': ('user_info_display',)}),
        ('This Exchange', {'fields': ('message', 'response', 'intent', 'confidence', 'created_at')}),
        ('Full Conversation', {'fields': ('full_conversation',)}),
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
