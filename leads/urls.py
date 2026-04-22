from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet
import json

router = DefaultRouter()
router.register(r'', LeadViewSet, basename='lead')


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def newsletter_subscribe(request):
    """Standalone newsletter subscription — separate from the lead router."""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        body = json.loads(request.body)
        email = body.get('email', '').strip().lower()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not email:
        return JsonResponse({'email': ['This field is required.']}, status=400)

    from .models import NewsletterSubscription
    subscription, created = NewsletterSubscription.objects.get_or_create(
        email=email,
        defaults={'status': 'ACTIVE'}
    )

    if not created and subscription.status == 'UNSUBSCRIBED':
        subscription.status = 'ACTIVE'
        subscription.save()

    return JsonResponse({
        'id': subscription.id,
        'email': subscription.email,
        'status': subscription.status,
        'subscribed_at': subscription.subscribed_at.isoformat(),
    }, status=201)


urlpatterns = [
    path('', include(router.urls)),
]

# Exported separately — registered in realtor_pal/urls.py as api/newsletter/
newsletter_urlpatterns = [
    path('', newsletter_subscribe, name='newsletter-subscribe'),
]
