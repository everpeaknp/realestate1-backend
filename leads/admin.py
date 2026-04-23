from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from .models import Lead, NewsletterSubscription


# ------------------------------------------------------------------ #
#  Analytics view                                                      #
# ------------------------------------------------------------------ #

def lead_analytics_view(request):
    """Full analytics dashboard for leads — rendered inside Django admin."""
    # Must be staff
    if not request.user.is_staff:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    now = timezone.now()
    today = now.date()
    last_30 = today - timedelta(days=29)
    last_7  = today - timedelta(days=6)

    all_leads = Lead.objects.all()
    total     = all_leads.count()
    new_count = all_leads.filter(status='NEW').count()
    contacted = all_leads.filter(status='CONTACTED').count()
    qualified = all_leads.filter(status='QUALIFIED').count()
    closed    = all_leads.filter(status='CLOSED').count()

    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    this_month = all_leads.filter(created_at__gte=this_month_start).count()
    last_month = all_leads.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).count()
    month_change = this_month - last_month
    month_pct = round((month_change / last_month * 100) if last_month else 0, 1)

    today_count = all_leads.filter(created_at__date=today).count()
    week_count  = all_leads.filter(created_at__date__gte=last_7).count()

    # Conversion rate: closed / total
    conversion_rate = round((closed / total * 100) if total else 0, 1)

    # Newsletter
    newsletter_total  = NewsletterSubscription.objects.count()
    newsletter_active = NewsletterSubscription.objects.filter(status='ACTIVE').count()

    # Most inquired property
    from properties.models import Property as PropertyModel
    from django.db.models import Count as DjCount
    most_inquired = (
        all_leads.exclude(related_property=None)
        .values('related_property__title', 'related_property__slug')
        .annotate(inq=DjCount('id'))
        .order_by('-inq')
        .first()
    )
    most_inquired_title = most_inquired['related_property__title'] if most_inquired else 'N/A'
    most_inquired_count = most_inquired['inq'] if most_inquired else 0

    # --- By inquiry type ---
    by_type = list(
        all_leads.values('inquiry_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    type_labels = [t['inquiry_type'].replace('_', ' ').title() for t in by_type]
    type_data   = [t['count'] for t in by_type]
    type_colors = ['#007bff', '#28a745', '#17a2b8', '#ffc107', '#6c757d']

    # --- By source ---
    by_source = list(
        all_leads.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    source_labels = [s['source'].replace('_', ' ').title() for s in by_source]
    source_data   = [s['count'] for s in by_source]
    source_colors = ['#c1a478', '#5d6d87', '#28a745', '#dc3545']

    # --- By status ---
    status_data_map = {
        'NEW': new_count,
        'CONTACTED': contacted,
        'QUALIFIED': qualified,
        'CLOSED': closed,
    }

    # --- Daily trend (last 30 days) ---
    daily_qs = (
        all_leads
        .filter(created_at__date__gte=last_30)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    daily_map = {str(r['day']): r['count'] for r in daily_qs}
    trend_labels = []
    trend_data   = []
    for i in range(30):
        d = last_30 + timedelta(days=i)
        trend_labels.append(d.strftime('%b %d'))
        trend_data.append(daily_map.get(str(d), 0))

    # --- Monthly trend (last 12 months) ---
    monthly_qs = (
        all_leads
        .filter(created_at__gte=now - timedelta(days=365))
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_labels = [r['month'].strftime('%b %Y') for r in monthly_qs]
    monthly_data   = [r['count'] for r in monthly_qs]

    # --- Top locations ---
    top_locations_raw = list(
        all_leads
        .exclude(location='')
        .values('location')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )
    max_loc = top_locations_raw[0]['count'] if top_locations_raw else 1
    top_locations = [
        {**loc, 'pct': round(loc['count'] / max_loc * 100)}
        for loc in top_locations_raw
    ]

    # --- Recent leads ---
    recent_leads = all_leads.select_related('related_property')[:10]

    context = {
        # KPIs
        'total': total,
        'new_count': new_count,
        'contacted': contacted,
        'qualified': qualified,
        'closed': closed,
        'today_count': today_count,
        'week_count': week_count,
        'this_month': this_month,
        'last_month': last_month,
        'month_change': month_change,
        'month_pct': month_pct,
        'conversion_rate': conversion_rate,
        'newsletter_total': newsletter_total,
        'newsletter_active': newsletter_active,
        'today_count': today_count,
        'week_count': week_count,
        'most_inquired_title': most_inquired_title,
        'most_inquired_count': most_inquired_count,

        # Chart data (JSON)
        'type_labels_json':   json.dumps(type_labels),
        'type_data_json':     json.dumps(type_data),
        'type_colors_json':   json.dumps(type_colors[:len(type_data)]),
        'source_labels_json': json.dumps(source_labels),
        'source_data_json':   json.dumps(source_data),
        'source_colors_json': json.dumps(source_colors[:len(source_data)]),
        'status_labels_json': json.dumps(['New', 'Contacted', 'Qualified', 'Closed']),
        'status_data_json':   json.dumps([new_count, contacted, qualified, closed]),
        'trend_labels_json':  json.dumps(trend_labels),
        'trend_data_json':    json.dumps(trend_data),
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_data_json':   json.dumps(monthly_data),

        # Tables
        'top_locations': top_locations,
        'recent_leads':  recent_leads,

        # Admin context — required for sidebar, breadcrumbs, and Jazzmin layout
        'title': 'Lead Analytics',
        'opts': Lead._meta,
        'app_label': 'leads',
        'has_permission': True,
        'is_popup': False,
        'is_nav_sidebar_enabled': True,
        'available_apps': admin.site.get_app_list(request),
    }
    return render(request, 'admin/leads/analytics.html', context)


# ------------------------------------------------------------------ #
#  Lead Admin                                                          #
# ------------------------------------------------------------------ #

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Enhanced admin for Lead model with analytics dashboard."""
    list_display = (
        'full_name', 'email', 'phone', 'inquiry_type_badge',
        'source_badge', 'status_badge', 'property_link', 'created_at'
    )
    list_filter = ('inquiry_type', 'source', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'message', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'location', 'subject', 'message')
        }),
        ('Interest / Preferences', {
            'fields': ('budget', 'property_type_interest'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('source', 'related_property', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('analytics/', self.admin_site.admin_view(lead_analytics_view), name='leads_lead_analytics'),
        ]
        return custom + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['analytics_url'] = '../analytics/'
        # Quick KPIs for the list header
        total = Lead.objects.count()
        new_c = Lead.objects.filter(status='NEW').count()
        extra_context['quick_total'] = total
        extra_context['quick_new']   = new_c
        return super().changelist_view(request, extra_context=extra_context)

    # ---- Display methods ----

    def inquiry_type_badge(self, obj):
        colors = {
            'BUYING':    '#007bff',
            'SELLING':   '#28a745',
            'RENTING':   '#17a2b8',
            'HOME_LOAN': '#ffc107',
            'GENERAL':   '#6c757d',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;font-size:11px;">{}</span>',
            colors.get(obj.inquiry_type, '#6c757d'),
            obj.get_inquiry_type_display()
        )
    inquiry_type_badge.short_description = 'Inquiry Type'
    inquiry_type_badge.admin_order_field = 'inquiry_type'

    def source_badge(self, obj):
        source_labels = {
            'CONTACT_FORM':     'Form',
            'CHATBOT':          'Chat',
            'PROPERTY_INQUIRY': 'Property',
            'NEWSLETTER':       'Newsletter',
            'VALUATION':        'Valuation',
        }
        source_colors = {
            'CONTACT_FORM':     '#17a2b8',
            'CHATBOT':          '#6f42c1',
            'PROPERTY_INQUIRY': '#28a745',
            'NEWSLETTER':       '#fd7e14',
            'VALUATION':        '#c1a478',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;font-size:11px;">{}</span>',
            source_colors.get(obj.source, '#6c757d'),
            source_labels.get(obj.source, obj.get_source_display())
        )
    source_badge.short_description = 'Source'
    source_badge.admin_order_field = 'source'

    def status_badge(self, obj):
        colors = {
            'NEW':       '#dc3545',
            'CONTACTED': '#ffc107',
            'QUALIFIED': '#17a2b8',
            'CLOSED':    '#28a745',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;font-size:11px;font-weight:bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def property_link(self, obj):
        prop = obj.related_property
        if prop:
            return format_html(
                '<a href="/admin/properties/property/{}/change/" style="color:#007bff;text-decoration:none;">{}</a>',
                prop.id,
                prop.title[:30] + '...' if len(prop.title) > 30 else prop.title
            )
        return format_html('<span style="color:#999;">-</span>')
    property_link.short_description = 'Property'

    actions = ['mark_as_contacted', 'mark_as_qualified', 'mark_as_closed']

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='CONTACTED')
        self.message_user(request, f'{updated} leads marked as contacted.', 'success')
    mark_as_contacted.short_description = 'Mark as contacted'

    def mark_as_qualified(self, request, queryset):
        updated = queryset.update(status='QUALIFIED')
        self.message_user(request, f'{updated} leads marked as qualified.', 'success')
    mark_as_qualified.short_description = 'Mark as qualified'

    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(request, f'{updated} leads marked as closed.', 'success')
    mark_as_closed.short_description = 'Mark as closed'


# ------------------------------------------------------------------ #
#  Newsletter Admin                                                    #
# ------------------------------------------------------------------ #

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status_badge', 'subscribed_at')
    list_filter = ('status', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    date_hierarchy = 'subscribed_at'
    list_per_page = 100

    def status_badge(self, obj):
        colors = {'ACTIVE': '#28a745', 'UNSUBSCRIBED': '#6c757d'}
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;font-size:11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    actions = ['mark_as_active', 'mark_as_unsubscribed']

    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} subscriptions marked as active.', 'success')
    mark_as_active.short_description = '✓ Mark as active'

    def mark_as_unsubscribed(self, request, queryset):
        updated = queryset.update(status='UNSUBSCRIBED')
        self.message_user(request, f'{updated} subscriptions marked as unsubscribed.', 'warning')
    mark_as_unsubscribed.short_description = '✗ Mark as unsubscribed'
