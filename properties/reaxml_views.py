from __future__ import annotations

from decimal import Decimal

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ExternalPropertyFeed


STATUS_ALIASES = {
    'FOR_SALE': 'CURRENT',
    'AVAILABLE': 'CURRENT',
    'UNDER OFFER': 'UNDER_OFFER',
    'UNDER_OFFER': 'UNDER_OFFER',
    'PENDING': 'UNDER_OFFER',
    'RENTED': 'LEASED',
}


def _decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _agent_payload(record: ExternalPropertyFeed) -> list[dict]:
    if not (record.agent_name or record.agent_email or record.agent_phone or record.agent_mobile):
        return []

    return [
        {
            'id': record.agent_id or '1',
            'name': record.agent_name or 'Agent',
            'email': record.agent_email or None,
            'phone': record.agent_phone or None,
            'mobile': record.agent_mobile or None,
            'title': None,
            'avatarUrl': None,
        }
    ]


def _inspection_payload(record: ExternalPropertyFeed) -> dict:
    nodes = []
    for index, item in enumerate(record.inspection_times or [], start=1):
        nodes.append(
            {
                'id': str(item.get('id') or index),
                'start': item.get('start') or None,
                'finish': item.get('finish') or None,
            }
        )
    return {'nodes': nodes}


def _media_payload(items: list[dict]) -> list[dict]:
    result: list[dict] = []
    for index, item in enumerate(items or [], start=1):
        url = (item.get('url') or '').strip()
        if not url:
            continue
        result.append({'id': str(item.get('id') or index), 'url': url})
    return result


def _as_eagle_property(record: ExternalPropertyFeed) -> dict:
    images = _media_payload(record.image_urls)
    floorplans = _media_payload(record.floorplan_urls)

    return {
        'id': record.external_id,
        'formattedAddress': record.formatted_address,
        'latitude': _decimal_to_float(record.latitude),
        'longitude': _decimal_to_float(record.longitude),
        'propertyType': record.property_type or None,
        'status': record.status,
        'price': _decimal_to_float(record.price),
        'advertisedPrice': record.advertised_price or None,
        'description': record.description or None,
        'headline': record.headline or None,
        'featured': record.featured,
        'landSize': record.land_size or None,
        'landSizeUnits': record.land_size_units or None,
        'thumbnailSquare': images[0]['url'] if images else None,
        'images': images,
        'floorplans': floorplans,
        'vendors': [],
        'agents': _agent_payload(record),
        'inspections': _inspection_payload(record),
        'createdAt': record.created_at.isoformat(),
        'updatedAt': record.updated_at.isoformat(),
        # Extended fields used by some UI logic.
        'beds': record.bedrooms,
        'baths': _decimal_to_float(record.bathrooms),
        'cars': record.garages,
    }


def _normalize_status(raw_status: str | None) -> str | None:
    if not raw_status:
        return None
    upper = raw_status.strip().upper()
    return STATUS_ALIASES.get(upper, upper.replace('-', '_').replace(' ', '_'))


@require_http_methods(['GET'])
def reaxml_properties(request):
    limit_raw = request.GET.get('limit', '50')
    search = (request.GET.get('search') or '').strip()
    status = _normalize_status(request.GET.get('status'))
    property_type = (request.GET.get('propertyType') or request.GET.get('property_type') or '').strip().upper()
    agent_name = (request.GET.get('agentName') or '').strip()

    try:
        limit = max(1, min(int(limit_raw), 500))
    except ValueError:
        limit = 50

    queryset = ExternalPropertyFeed.objects.filter(is_active=True)

    if status:
        queryset = queryset.filter(status=status)
    if property_type:
        queryset = queryset.filter(property_type=property_type)
    if agent_name:
        queryset = queryset.filter(agent_name__icontains=agent_name)
    if search:
        queryset = queryset.filter(
            Q(formatted_address__icontains=search)
            | Q(headline__icontains=search)
            | Q(description__icontains=search)
            | Q(suburb__icontains=search)
        )

    listings = list(queryset.order_by('-updated_at')[:limit])
    payload = [_as_eagle_property(item) for item in listings]

    return JsonResponse(
        {
            'success': True,
            'count': len(payload),
            'properties': payload,
            'source': 'REAXML',
        }
    )


@require_http_methods(['GET'])
def reaxml_property_detail(request, property_id: str):
    try:
        listing = ExternalPropertyFeed.objects.get(external_id=property_id, is_active=True)
    except ExternalPropertyFeed.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found'}, status=404)

    return JsonResponse({'success': True, 'property': _as_eagle_property(listing), 'source': 'REAXML'})


@require_http_methods(['GET'])
def reaxml_health(request):
    total = ExternalPropertyFeed.objects.filter(is_active=True).count()
    latest = ExternalPropertyFeed.objects.order_by('-updated_at').first()

    return JsonResponse(
        {
            'success': True,
            'source': 'REAXML',
            'activeListings': total,
            'latestUpdateAt': latest.updated_at.isoformat() if latest else None,
        }
    )
