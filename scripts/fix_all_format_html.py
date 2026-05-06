#!/usr/bin/env python
"""
Comprehensive fix for all format_html calls in Django 6.0.
This script fixes static strings in format_html calls.
"""

import os
import re

# Mapping of files and their fixes
FIXES = {
    'properties/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No image</p>'\)", 
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image')"),
        (r"format_html\('<span style=\"color: #999;\">No image</span>'\)",
         "format_html('<span style=\"color: #999;\">{}</span>', 'No image')"),
        (r"format_html\('<span style=\"color: #ffc107; font-size: 18px;\">★</span>'\)",
         "format_html('<span style=\"color: #ffc107; font-size: 18px;\">{}</span>', '★')"),
        (r"format_html\('<span style=\"color: #ddd; font-size: 18px;\">☆</span>'\)",
         "format_html('<span style=\"color: #ddd; font-size: 18px;\">{}</span>', '☆')"),
        (r"format_html\('<p style=\"color: #999;\">No image uploaded</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image uploaded')"),
        (r"format_html\('<p style=\"color: #999;\">No floor plan uploaded</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No floor plan uploaded')"),
    ],
    'services/admin.py': [
        (r"format_html\('<span style=\"color: #28a745; font-size: 18px;\">✓</span>'\)",
         "format_html('<span style=\"color: #28a745; font-size: 18px;\">{}</span>', '✓')"),
        (r"format_html\('<span style=\"color: #dc3545; font-size: 18px;\">✗</span>'\)",
         "format_html('<span style=\"color: #dc3545; font-size: 18px;\">{}</span>', '✗')"),
    ],
    'projects/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No background image</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No background image')"),
    ],
    'faqs/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No background image</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No background image')"),
        (r"format_html\('<span style=\"color: #28a745; font-size: 18px;\">✓</span>'\)",
         "format_html('<span style=\"color: #28a745; font-size: 18px;\">{}</span>', '✓')"),
        (r"format_html\('<span style=\"color: #dc3545; font-size: 18px;\">✗</span>'\)",
         "format_html('<span style=\"color: #dc3545; font-size: 18px;\">{}</span>', '✗')"),
    ],
    'gallery/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No image</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image')"),
        (r"format_html\('<span style=\"color: #999;\">📷</span>'\)",
         "format_html('<span style=\"color: #999;\">{}</span>', '📷')"),
        (r"format_html\('<span style=\"color: #999;\">No file</span>'\)",
         "format_html('<span style=\"color: #999;\">{}</span>', 'No file')"),
        (r"format_html\('<span style=\"color: #999;\">Not attached</span>'\)",
         "format_html('<span style=\"color: #999;\">{}</span>', 'Not attached')"),
        (r"format_html\('<p style=\"color: #999;\">No image uploaded</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image uploaded')"),
        (r"format_html\('<span style=\"color: #999;\">—</span>'\)",
         "format_html('<span style=\"color: #999;\">{}</span>', '—')"),
    ],
    'leads/admin.py': [
        (r"format_html\('<span style=\"color:#999;\">-</span>'\)",
         "format_html('<span style=\"color:#999;\">{}</span>', '-')"),
        (r"format_html\('<span style=\"color: #999; font-style: italic;\">No image</span>'\)",
         "format_html('<span style=\"color: #999; font-style: italic;\">{}</span>', 'No image')"),
    ],
    'about/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No image</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image')"),
    ],
    'blog/admin.py': [
        (r"format_html\('<p style=\"color: #999;\">No image</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image')"),
        (r"format_html\('<span style=\"color: #28a745; font-size: 18px;\">✓</span>'\)",
         "format_html('<span style=\"color: #28a745; font-size: 18px;\">{}</span>', '✓')"),
        (r"format_html\('<span style=\"color: #dc3545; font-size: 18px;\">✗</span>'\)",
         "format_html('<span style=\"color: #dc3545; font-size: 18px;\">{}</span>', '✗')"),
        (r"format_html\('<p style=\"color: #999;\">No image uploaded</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No image uploaded')"),
        (r"format_html\('<p style=\"color: #999;\">No avatar uploaded</p>'\)",
         "format_html('<p style=\"color: #999;\">{}</p>', 'No avatar uploaded')"),
    ],
}

def fix_file(filepath, fixes):
    """Apply fixes to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except FileNotFoundError:
        return False

def main():
    print("=" * 80)
    print("FIXING ALL format_html CALLS FOR DJANGO 6.0")
    print("=" * 80)
    
    fixed_count = 0
    for filepath, fixes in FIXES.items():
        if fix_file(filepath, fixes):
            print(f"✅ Fixed: {filepath}")
            fixed_count += 1
        else:
            print(f"⏭️  Skipped: {filepath} (no changes or not found)")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Fixed {fixed_count} files")
    print("=" * 80)
    print("\n🔄 Please restart your Django server for changes to take effect!")

if __name__ == '__main__':
    main()
