from django.conf import settings
from decouple import config

def get_absolute_media_url(url):
    """
    Ensures a media URL is absolute and uses the public BASE_URL if configured.
    This prevents internal Docker hostnames (like realestate1-backend:8000) 
    from leaking into the frontend.
    """
    if not url:
        return None
        
    if url.startswith('http'):
        # If it's already absolute, check if it contains internal hostnames
        internal_hosts = ['realestate1-backend', '127.0.0.1', 'localhost', '0.0.0.0']
        if any(host in url for host in internal_hosts):
            # Extract the path after /media/
            if '/media/' in url:
                path = url.split('/media/')[-1]
                base_url = config('BASE_URL', default='').rstrip('/')
                if base_url:
                    return f"{base_url}/media/{path}"
                return f"/media/{path}" # Fallback to relative
        return url

    # If it's relative, prepend BASE_URL if in production
    base_url = config('BASE_URL', default='').rstrip('/')
    if base_url:
        if url.startswith('/'):
            return f"{base_url}{url}"
        return f"{base_url}/{url}"
        
    return url
