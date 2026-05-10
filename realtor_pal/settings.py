"""
Django settings for Lily White Realestate project.
"""

"""
Django Settings v1.1 - Triggering CI/CD Test
"""
from pathlib import Path
from decouple import config
import dj_database_url
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') if h.strip()]

# Automatically add Render's external hostname to ALLOWED_HOSTS
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Professional admin theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_ckeditor_5',
    
    # Local apps
    'properties',
    'leads',
    'blog',
    'gallery',
    'testimonials',
    'projects',
    'faqs',
    'agents',
    'chatbot',
    'about',
    'contact',
    'cms',
    'home',
    'homeworth',
    'services',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise
    # 'realtor_pal.middleware.MediaFilesMiddleware',  # TEMPORARILY DISABLED - May interfere with context
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise configuration for serving media files in production
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

ROOT_URLCONF = 'realtor_pal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'builtins': [
            #     'realtor_pal.templatetags.jazzmin_compat',  # DISABLED - Causing context issues
            # ],
        },
    },
]

WSGI_APPLICATION = 'realtor_pal.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# If in production and BASE_URL is provided, force MEDIA_URL to be absolute
# This prevents internal Docker hostnames from leaking into the frontend
BASE_URL = config('BASE_URL', default=None)
if not DEBUG and BASE_URL:
    BASE_URL = BASE_URL.rstrip('/')
    if not MEDIA_URL.startswith('http'):
        MEDIA_URL = f"{BASE_URL}{MEDIA_URL}"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://127.0.0.1:3000'
    ).split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins (required when Django is behind HTTPS reverse proxy)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CSRF_TRUSTED_ORIGINS',
        default='http://localhost:3000,http://127.0.0.1:3000'
    ).split(',')
    if origin.strip()
]

# Trust HTTPS termination done at reverse proxy (Nginx/Caddy)
# This ensures Django uses the correct public hostname and protocol
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'realtor_pal.pagination.DynamicPageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Spectacular settings (API documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lily White Realestate API',
    'DESCRIPTION': 'Real Estate Platform API',
    'VERSION': '1.0.0',
}

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "Lily White Realestate Admin",
    "site_header": "Lily White Realestate",
    "site_brand": "Lily White Realestate",
    "site_logo": None,
    "welcome_sign": "Welcome to Lily White Realestate Admin",
    "copyright": "Lily White Realestate Ltd",
    "search_model": ["properties.Property", "leads.Lead", "blog.BlogPost"],
    
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/schema/swagger-ui/", "new_window": True},
        {"name": "Lead Analytics", "url": "/admin/leads/lead/analytics/", "permissions": ["leads.view_lead"]},
        {"model": "properties.Property"},
        {"model": "leads.Lead"},
    ],
    
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [
        "properties.PropertiesHeroSettings",
        "properties.PropertyImage",
        "home.InstagramImage",
    ],
    "order_with_respect_to": [
        "properties",
        "properties.Property",
        "leads",
        "blog",
        "gallery",
        "testimonials",
        "projects",
        "faqs",
        "agents",
        "chatbot",
        "services",
        "about",
        "contact",
        "cms",
        "home",
    ],
    
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "properties.Property": "fas fa-home",
        "leads.Lead": "fas fa-user-plus",
        "leads.NewsletterSubscription": "fas fa-envelope",
        "blog.BlogPost": "fas fa-blog",
        "blog.Comment": "fas fa-comments",
        "gallery.GalleryImage": "fas fa-images",
        "testimonials.Testimonial": "fas fa-star",
        "projects.Project": "fas fa-project-diagram",
        "faqs.FAQ": "fas fa-question-circle",
        "agents.Agent": "fas fa-user-tie",
        "chatbot.ChatSession": "fas fa-comments",
        "chatbot.ChatMessage": "fas fa-comment-dots",
        "chatbot.KnowledgeBase": "fas fa-brain",
        "chatbot.ChatbotRule": "fas fa-code-branch",
        "chatbot.ChatbotSettings": "fas fa-toggle-on",
        "services.Service": "fas fa-concierge-bell",
        "about.Goal": "fas fa-bullseye",
        "about.ServicesProvide": "fas fa-hands-helping",
        "contact.ContactCard": "fas fa-address-card",
        "contact.ContactFormSettings": "fas fa-cog",
        "cms.HeaderSettings": "fas fa-heading",
        "cms.NavigationLink": "fas fa-link",
        "cms.FooterSettings": "fas fa-shoe-prints",
        "cms.FooterLink": "fas fa-external-link-alt",
        "home.HeroSettings": "fas fa-image",
        "home.HeroCard": "fas fa-th-large",
        "home.HowItWorksStep": "fas fa-tasks",
        "home.Neighborhood": "fas fa-map-marked-alt",
        "home.BenefitsSection": "fas fa-star",
        "home.ContactSectionSettings": "fas fa-id-card",
        "home.InstagramImage": "fab fa-instagram",
        "home.PersonSectionSettings": "fas fa-user-circle",
        "home.StatItem": "fas fa-chart-line",
    },

    "custom_links": {
        "leads": [
            {
                "name": "Lead Analytics",
                "url": "/admin/leads/lead/analytics/",
                "icon": "fas fa-chart-bar",
                "permissions": ["leads.view_lead"],
            }
        ],
        "properties": [
            {
                "name": "Property Images",
                "url": "/admin/properties/propertyimage/",
                "icon": "fas fa-images",
                "permissions": ["properties.view_propertyimage"],
            },
            {
                "name": "Hero Settings",
                "url": "/admin/properties/propertiesherosettings/",
                "icon": "fas fa-sliders-h",
                "permissions": ["properties.view_propertiesherosettings"],
            },
        ],
    },
    
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    "related_modal_active": False,
    "custom_css": "admin/css/ckeditor_custom.css",
    "custom_js": "admin/js/ckeditor_fullscreen.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    "changeform_format": "collapsible",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "collapsible"
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-navy",
    "accent": "accent-olive",
    "navbar": "navbar-navy navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-olive",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# CKEditor 5 Configuration
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
