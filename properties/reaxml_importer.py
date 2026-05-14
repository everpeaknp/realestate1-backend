"""
REAXML feed importer for Eagle CRM listing exports.

Responsibilities:
1. Retrieve XML files (from FTP or local directory).
2. Parse REAXML listing payloads.
3. Upsert normalized listing records into ExternalPropertyFeed.
"""

from __future__ import annotations

import ftplib
import hashlib
import io
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from django.conf import settings

from .models import ExternalPropertyFeed


INACTIVE_STATUSES = {'DELETED', 'WITHDRAWN', 'OFFMARKET'}


def _tag_name(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag


def _direct_child(node: ET.Element, name: str) -> ET.Element | None:
    for child in list(node):
        if _tag_name(child.tag).lower() == name.lower():
            return child
    return None


def _iter_named(node: ET.Element, name: str) -> Iterable[ET.Element]:
    for el in node.iter():
        if _tag_name(el.tag).lower() == name.lower():
            yield el


def _first_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        for el in _iter_named(node, name):
            value = (el.text or '').strip()
            if value:
                return value
    return ''


def _first_attr(node: ET.Element, names: list[str], attrs: list[str]) -> str:
    for name in names:
        for el in _iter_named(node, name):
            for attr in attrs:
                value = (el.attrib.get(attr) or '').strip()
                if value:
                    return value
    return ''


def _to_decimal(value: str) -> Decimal | None:
    if not value:
        return None

    cleaned = re.sub(r'[^0-9.+-]', '', value)
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _to_int(value: str) -> int | None:
    if not value:
        return None
    match = re.search(r'-?\d+', value)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _normalize_property_type(value: str, listing_type: str) -> str:
    normalized = re.sub(r'[^A-Z0-9]+', '_', value.upper()).strip('_')
    if normalized:
        return normalized
    return listing_type.upper()


def _normalize_status(raw_status: str, under_offer: str) -> str:
    status = re.sub(r'[^A-Z0-9]+', '_', raw_status.upper()).strip('_') or 'CURRENT'
    if status == 'CURRENT' and under_offer.lower() == 'yes':
        return 'UNDER_OFFER'
    if status == 'RENTED':
        return 'LEASED'
    return status


def _is_featured(listing: ET.Element) -> bool:
    featured_attr = _first_attr(listing, ['featured', 'featureListing'], ['value', 'featured'])
    if featured_attr.lower() in {'yes', 'true', '1'}:
        return True

    # Some feeds mark featured via <listingAgent marketing="featured"> style attrs.
    for key in ['featured', 'feature', 'marketing']:
        value = _first_attr(listing, ['listingAgent', 'agent', 'listing'], [key])
        if value.lower() in {'yes', 'true', '1', 'featured'}:
            return True
    return False


def _extract_address(listing: ET.Element) -> tuple[str, str, str, str]:
    address = _direct_child(listing, 'address')
    if address is None:
        formatted = _first_text(listing, ['formattedAddress', 'address'])
        return formatted, '', '', ''

    display = (address.attrib.get('display') or '').strip()
    display_flag = display.lower()
    suburb = (address.attrib.get('suburb') or _first_text(address, ['suburb'])).strip()
    state = (address.attrib.get('state') or _first_text(address, ['state'])).strip()
    postcode = (address.attrib.get('postcode') or _first_text(address, ['postcode', 'postCode'])).strip()

    # In REAXML, address.display is commonly a visibility flag (yes/no), not
    # a formatted address string. Only trust it as an address when it is not a
    # boolean-like value.
    if display and display_flag not in {'yes', 'no', 'true', 'false', '1', '0'}:
        return display, suburb, state, postcode

    unit = _first_text(address, ['unitNumber', 'unit'])
    street_number = _first_text(address, ['streetNumber', 'streetNo'])
    street_name = _first_text(address, ['street', 'streetName'])

    street_parts = [part for part in [unit, street_number, street_name] if part]
    street_line = ' '.join(street_parts).strip()

    locality_parts = [part for part in [suburb, state, postcode] if part]
    locality = ', '.join(locality_parts).strip()

    # Respect hidden street-address feeds (display=no/false/0) by returning
    # only suburb/state/postcode when possible.
    if display_flag in {'no', 'false', '0'} and locality:
        return locality, suburb, state, postcode

    if street_line and locality:
        return f'{street_line}, {locality}', suburb, state, postcode
    if street_line:
        return street_line, suburb, state, postcode
    return locality, suburb, state, postcode


def _extract_media(listing: ET.Element, container_names: list[str], item_names: list[str]) -> list[dict]:
    collected: list[dict] = []
    seen: set[str] = set()

    containers: list[ET.Element] = []
    for name in container_names:
        containers.extend(_iter_named(listing, name))
    if not containers:
        containers = [listing]

    for container in containers:
        for item_name in item_names:
            for media in _iter_named(container, item_name):
                url = (
                    media.attrib.get('url')
                    or media.attrib.get('href')
                    or media.attrib.get('src')
                    or (media.text or '').strip()
                )
                if not url or url in seen:
                    continue
                seen.add(url)
                collected.append(
                    {
                        'id': (media.attrib.get('id') or str(len(collected) + 1)).strip(),
                        'url': url.strip(),
                    }
                )
    return collected


def _extract_inspections(listing: ET.Element) -> list[dict]:
    nodes: list[dict] = []
    for inspection in _iter_named(listing, 'inspection'):
        start = (
            inspection.attrib.get('start')
            or inspection.attrib.get('from')
            or _first_text(inspection, ['start', 'startTime', 'from'])
        ).strip()
        finish = (
            inspection.attrib.get('finish')
            or inspection.attrib.get('to')
            or _first_text(inspection, ['finish', 'end', 'to'])
        ).strip()
        if start or finish:
            nodes.append(
                {
                    'id': (inspection.attrib.get('id') or str(len(nodes) + 1)).strip(),
                    'start': start,
                    'finish': finish,
                }
            )
    return nodes


def _append_stats_description(description: str, beds: int | None, baths: Decimal | None, garages: int | None) -> str:
    lines = [description.strip()] if description.strip() else []
    if beds is not None:
        lines.append(f'• {beds} Bedrooms')
    if baths is not None:
        baths_text = format(baths, 'f').rstrip('0').rstrip('.') or '0'
        lines.append(f'• {baths_text} Bathrooms')
    if garages is not None:
        lines.append(f'• {garages} Car Spaces')
    return '\n'.join(lines).strip()


@dataclass
class ReaxmlFile:
    name: str
    content: str


def _extract_coordinates(listing: ET.Element) -> tuple[Decimal | None, Decimal | None]:
    # 1) Direct coordinate tags
    latitude = _to_decimal(
        _first_text(
            listing,
            ['latitude', 'lat', 'geoLatitude', 'geo_latitude'],
        )
    )
    longitude = _to_decimal(
        _first_text(
            listing,
            ['longitude', 'long', 'lon', 'lng', 'geoLongitude', 'geo_longitude'],
        )
    )
    if latitude is not None and longitude is not None:
        return latitude, longitude

    # 2) Coordinate attributes on common location nodes
    lat_attr = _first_attr(
        listing,
        ['address', 'geolocation', 'geoLocation', 'location', 'position', 'coordinates'],
        ['latitude', 'lat', 'y'],
    )
    lng_attr = _first_attr(
        listing,
        ['address', 'geolocation', 'geoLocation', 'location', 'position', 'coordinates'],
        ['longitude', 'long', 'lon', 'lng', 'x'],
    )
    lat_from_attr = _to_decimal(lat_attr)
    lng_from_attr = _to_decimal(lng_attr)
    if lat_from_attr is not None and lng_from_attr is not None:
        return lat_from_attr, lng_from_attr

    # 3) Combined coordinate text, e.g. "-33.86,151.20" or "151.20 -33.86"
    combined = _first_text(
        listing,
        ['geolocation', 'geoLocation', 'coordinates', 'position', 'point', 'latlng', 'longlat'],
    )
    if combined:
        nums = re.findall(r'-?\d+(?:\.\d+)?', combined)
        if len(nums) >= 2:
            first = _to_decimal(nums[0])
            second = _to_decimal(nums[1])
            if first is not None and second is not None:
                # If the first value cannot be latitude, treat as lon,lat.
                if abs(first) > 90 and abs(second) <= 90:
                    return second, first
                return first, second

    # Partial fallback if only one side was found in tags.
    if latitude is not None or longitude is not None:
        return latitude, longitude
    return None, None


def _build_feed_signature(parts: list[str]) -> str:
    payload = '\n'.join(parts).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _default_signature_file() -> Path:
    media_root = str(getattr(settings, 'MEDIA_ROOT', '') or '').strip()
    base_dir = Path(media_root) if media_root else Path('/tmp')
    return base_dir / '.reaxml_feed_signature'


def _read_saved_signature(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8').strip()
    except OSError:
        return ''


def _write_saved_signature(path: Path, signature: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(signature, encoding='utf-8')


def parse_reaxml_file(xml_text: str, source_file: str = '') -> list[dict]:
    root = ET.fromstring(xml_text)
    listings: list[dict] = []
    listing_type_tags = {'residential', 'rental', 'commercial', 'rural', 'business', 'land', 'holiday'}

    listing_nodes = list(root)
    if _tag_name(root.tag).lower() in listing_type_tags:
        listing_nodes = [root]

    for listing in listing_nodes:
        listing_type = _tag_name(listing.tag).lower()
        if listing_type not in listing_type_tags:
            continue

        external_id = _first_text(listing, ['uniqueID', 'listingID', 'id'])
        agent_id = _first_text(listing, ['agentID'])
        if not external_id:
            # Fallback uniqueness for malformed feeds.
            synthetic = f'{source_file or "feed"}-{agent_id or "agent"}-{len(listings) + 1}'
            external_id = synthetic

        under_offer = _first_attr(listing, ['underOffer'], ['value'])
        status = _normalize_status(listing.attrib.get('status', ''), under_offer)

        category_el = _direct_child(listing, 'category')
        category_value = ''
        if category_el is not None:
            category_value = (category_el.attrib.get('name') or (category_el.text or '')).strip()
        property_type = _normalize_property_type(category_value, listing_type)

        formatted_address, suburb, state, postcode = _extract_address(listing)

        description = _first_text(listing, ['description', 'shortDescription', 'remarks'])
        headline = _first_text(listing, ['headline', 'title']) or formatted_address

        bedrooms = _to_int(_first_text(listing, ['bedrooms', 'bedRooms', 'bed']))
        bathrooms_raw = _first_text(listing, ['bathrooms', 'bathRooms', 'bath'])
        bathrooms = _to_decimal(bathrooms_raw)
        garages = _to_int(_first_text(listing, ['garages', 'carports', 'carSpaces', 'parking']))

        description_with_stats = _append_stats_description(description, bedrooms, bathrooms, garages)

        price_display = _first_attr(listing, ['price', 'sale', 'rent'], ['display', 'view'])
        price_candidates = [
            _first_text(listing, ['price']),
            _first_text(listing, ['value']),
            _first_text(listing, ['sale']),
            _first_text(listing, ['rent']),
            _first_text(listing, ['listingPrice']),
        ]
        parsed_price = None
        for candidate in price_candidates:
            parsed_price = _to_decimal(candidate)
            if parsed_price is not None:
                break
        if not price_display:
            for candidate in price_candidates:
                if candidate:
                    price_display = candidate.strip()
                    break

        land_size = _first_text(listing, ['land', 'landSize', 'landArea'])
        land_size_units = (
            _first_attr(listing, ['land', 'landSize', 'landArea'], ['units', 'unit'])
            or _first_text(listing, ['landSizeUnits', 'areaUnits'])
        )

        latitude, longitude = _extract_coordinates(listing)

        listing_agent = _direct_child(listing, 'listingAgent')
        agent_name = _first_text(listing_agent, ['name']) if listing_agent is not None else ''
        agent_email = _first_text(listing_agent, ['email']) if listing_agent is not None else ''
        agent_phone = _first_text(listing_agent, ['telephone', 'phone']) if listing_agent is not None else ''
        agent_mobile = _first_text(listing_agent, ['mobile']) if listing_agent is not None else ''

        images = _extract_media(listing, ['images', 'objects'], ['img', 'image'])
        floorplans = _extract_media(listing, ['floorplans', 'objects'], ['floorplan'])
        inspections = _extract_inspections(listing)

        is_active = status not in INACTIVE_STATUSES

        listings.append(
            {
                'external_id': external_id,
                'agent_id': agent_id,
                'listing_type': listing_type.upper(),
                'status': status,
                'property_type': property_type,
                'headline': headline,
                'description': description_with_stats,
                'formatted_address': formatted_address,
                'suburb': suburb,
                'state': state,
                'postcode': postcode,
                'latitude': latitude,
                'longitude': longitude,
                'price': parsed_price,
                'advertised_price': price_display,
                'land_size': land_size,
                'land_size_units': land_size_units,
                'featured': _is_featured(listing),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'garages': garages,
                'agent_name': agent_name,
                'agent_email': agent_email,
                'agent_phone': agent_phone,
                'agent_mobile': agent_mobile,
                'image_urls': images,
                'floorplan_urls': floorplans,
                'inspection_times': inspections,
                'raw_payload': {
                    'listing_type': listing_type,
                    'status': listing.attrib.get('status', ''),
                    'source_file': source_file,
                },
                'source_file': source_file,
                'is_active': is_active,
            }
        )

    return listings


def _read_local_files(directory: str) -> list[ReaxmlFile]:
    base = Path(directory)
    if not base.exists():
        return []

    files: list[ReaxmlFile] = []
    for file_path in sorted(base.glob('*.xml')):
        files.append(ReaxmlFile(name=file_path.name, content=file_path.read_text(encoding='utf-8', errors='ignore')))
    return files


def _local_feed_signature(directory: str, files: list[ReaxmlFile]) -> str:
    base = Path(directory)
    parts: list[str] = []
    for item in files:
        file_path = base / item.name
        try:
            stat = file_path.stat()
            parts.append(f'{item.name}|{stat.st_size}|{stat.st_mtime_ns}')
        except OSError:
            parts.append(f'{item.name}|0|0')
    return _build_feed_signature(parts)


def _read_ftp_files(previous_signature: str | None = None) -> tuple[list[ReaxmlFile], str, bool]:
    host = getattr(settings, 'REAXML_FTP_HOST', '').strip()
    username = getattr(settings, 'REAXML_FTP_USERNAME', '').strip()
    password = getattr(settings, 'REAXML_FTP_PASSWORD', '').strip()
    remote_path = getattr(settings, 'REAXML_FTP_PATH', '').strip() or '.'
    passive = getattr(settings, 'REAXML_FTP_PASSIVE', True)
    port = int(getattr(settings, 'REAXML_FTP_PORT', 21))

    if not host or not username or not password:
        return [], '', False

    ftp = ftplib.FTP()
    try:
        ftp.connect(host=host, port=port, timeout=30)
        ftp.login(user=username, passwd=password)
        ftp.set_pasv(passive)
        ftp.cwd(remote_path)

        entries = ftp.nlst()
        xml_names = sorted(name for name in entries if name.lower().endswith('.xml'))

        signature_parts: list[str] = []
        for name in xml_names:
            size = ''
            modified = ''
            try:
                size_value = ftp.size(name)
                if size_value is not None:
                    size = str(size_value)
            except ftplib.all_errors:
                size = ''

            try:
                response = ftp.sendcmd(f'MDTM {name}')
                tokens = response.strip().split()
                if len(tokens) >= 2 and tokens[0].startswith('213'):
                    modified = tokens[1]
            except ftplib.all_errors:
                modified = ''

            signature_parts.append(f'{name}|{size}|{modified}')

        signature = _build_feed_signature(signature_parts)
        if previous_signature and signature == previous_signature:
            return [], signature, True

        files: list[ReaxmlFile] = []
        for name in xml_names:
            buffer = io.BytesIO()
            ftp.retrbinary(f'RETR {name}', buffer.write)
            content = buffer.getvalue().decode('utf-8', errors='ignore')
            files.append(ReaxmlFile(name=name, content=content))

        return files, signature, False
    finally:
        try:
            ftp.quit()
        except ftplib.all_errors:
            try:
                ftp.close()
            except OSError:
                pass


def import_reaxml_feed(
    *,
    from_ftp: bool = False,
    local_dir: str | None = None,
    deactivate_missing: bool = False,
    dry_run: bool = False,
    skip_if_unchanged: bool = False,
    signature_file: str | None = None,
) -> dict:
    """
    Import REAXML listings and upsert into ExternalPropertyFeed.
    """

    signature_path = Path(signature_file).expanduser() if signature_file else _default_signature_file()
    previous_signature = _read_saved_signature(signature_path) if skip_if_unchanged else ''
    feed_signature = ''
    skipped_unchanged = False
    files: list[ReaxmlFile] = []
    source = ''

    if from_ftp:
        source = 'ftp'
        files, feed_signature, skipped_unchanged = _read_ftp_files(
            previous_signature=previous_signature if skip_if_unchanged else None
        )
    elif local_dir:
        source = local_dir
        files = _read_local_files(local_dir)
        feed_signature = _local_feed_signature(local_dir, files)
    else:
        default_dir = getattr(settings, 'REAXML_LOCAL_DIR', '').strip()
        if default_dir:
            source = default_dir
            files = _read_local_files(default_dir)
            feed_signature = _local_feed_signature(default_dir, files)

    if skip_if_unchanged and skipped_unchanged:
        return {
            'files_processed': 0,
            'records_parsed': 0,
            'created': 0,
            'updated': 0,
            'dry_run': dry_run,
            'source': source,
            'skipped_unchanged': True,
            'signature_file': str(signature_path),
        }

    if skip_if_unchanged and previous_signature and feed_signature and feed_signature == previous_signature:
        return {
            'files_processed': 0,
            'records_parsed': 0,
            'created': 0,
            'updated': 0,
            'dry_run': dry_run,
            'source': source,
            'skipped_unchanged': True,
            'signature_file': str(signature_path),
        }

    parsed_records: list[dict] = []
    for xml_file in files:
        try:
            parsed_records.extend(parse_reaxml_file(xml_file.content, source_file=xml_file.name))
        except ET.ParseError:
            # Skip malformed file while allowing others to import.
            continue

    seen_ids = {row['external_id'] for row in parsed_records}
    created = 0
    updated = 0

    if not dry_run:
        for payload in parsed_records:
            _, was_created = ExternalPropertyFeed.objects.update_or_create(
                external_id=payload['external_id'],
                defaults=payload,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if deactivate_missing and seen_ids:
            ExternalPropertyFeed.objects.exclude(external_id__in=seen_ids).update(is_active=False)
    else:
        existing_ids = set(
            ExternalPropertyFeed.objects.filter(external_id__in=seen_ids).values_list('external_id', flat=True)
        )
        for payload in parsed_records:
            if payload['external_id'] in existing_ids:
                updated += 1
            else:
                created += 1

    if skip_if_unchanged and feed_signature and not dry_run:
        _write_saved_signature(signature_path, feed_signature)

    return {
        'files_processed': len(files),
        'records_parsed': len(parsed_records),
        'created': created,
        'updated': updated,
        'dry_run': dry_run,
        'source': source or ('ftp' if from_ftp else (local_dir or getattr(settings, 'REAXML_LOCAL_DIR', ''))),
        'skipped_unchanged': False,
        'signature_file': str(signature_path) if skip_if_unchanged else None,
    }
