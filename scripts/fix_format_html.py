#!/usr/bin/env python
"""
Script to fix format_html calls for Django 6.0 compatibility.
Django 6.0 requires all format_html calls to have explicit placeholders.
"""

import os
import re

def fix_format_html_in_file(filepath):
    """Fix format_html calls in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Pattern 1: format_html('<tag>text</tag>') -> format_html('<tag>{}</tag>', 'text')
    # This handles static strings without any placeholders
    pattern1 = r"format_html\((['\"])(<[^>]+>)([^<{]*)(</[^>]+>)\1\)"
    
    def replace_static(match):
        quote = match.group(1)
        open_tag = match.group(2)
        text = match.group(3)
        close_tag = match.group(4)
        
        # Skip if already has placeholder
        if '{}' in text or '{' in text:
            return match.group(0)
        
        # Skip if text is empty or just whitespace
        if not text.strip():
            return match.group(0)
        
        changes.append(f"  Fixed: {match.group(0)[:60]}...")
        return f"format_html({quote}{open_tag}{{}}{close_tag}{quote}, {quote}{text}{quote})"
    
    content = re.sub(pattern1, replace_static, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    
    return []

def main():
    """Fix all admin.py files."""
    admin_files = []
    
    # Find all admin.py files
    for root, dirs, files in os.walk('.'):
        if 'admin.py' in files:
            filepath = os.path.join(root, 'admin.py')
            admin_files.append(filepath)
    
    print("=" * 80)
    print("FIXING format_html CALLS FOR DJANGO 6.0")
    print("=" * 80)
    
    total_changes = 0
    for filepath in admin_files:
        changes = fix_format_html_in_file(filepath)
        if changes:
            print(f"\n📝 {filepath}")
            for change in changes:
                print(change)
            total_changes += len(changes)
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Fixed {total_changes} format_html calls across {len([f for f in admin_files if fix_format_html_in_file(f)])} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
