"""
Custom middleware for serving media files in production.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.utils._os import safe_join
import os


class MediaFilesMiddleware:
    """
    Middleware to serve media files in production.
    This is necessary because Django's static() function doesn't work with WSGI servers like Gunicorn.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = settings.MEDIA_URL
        self.media_root = settings.MEDIA_ROOT
        
    def __call__(self, request):
        # Check if the request is for a media file
        if request.path.startswith(self.media_url):
            # Get the relative path after /media/
            relative_path = request.path[len(self.media_url):]
            
            # Build the full file path
            try:
                file_path = safe_join(str(self.media_root), relative_path)
            except ValueError:
                # Invalid path (e.g., contains ..)
                raise Http404("Invalid media file path")
            
            # Check if file exists
            if os.path.isfile(file_path):
                # Serve the file
                return FileResponse(open(file_path, 'rb'))
            else:
                raise Http404(f"Media file not found: {relative_path}")
        
        # Not a media file request, continue with normal processing
        response = self.get_response(request)
        return response
