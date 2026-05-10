"""
Blog search integration for chatbot.
Allows chatbot to search and recommend blog posts to users.
"""

import logging
from blog.models import BlogPost
from django.db.models import Q

logger = logging.getLogger(__name__)


def search_blog_posts(query: str, limit: int = 3) -> list:
    """
    Search blog posts by title, excerpt, content, or category.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of BlogPost objects matching the query
    """
    try:
        query_lower = query.lower()
        
        # Search in title, excerpt, content, category, and tags
        results = BlogPost.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-published_at')[:limit]
        
        logger.info(f"[BlogSearch] Found {results.count()} blog posts for query: {query}")
        return list(results)
        
    except Exception as e:
        logger.error(f"[BlogSearch] Error searching blog posts: {str(e)}")
        return []


def get_latest_blog_posts(limit: int = 3) -> list:
    """
    Get the latest published blog posts.
    
    Args:
        limit: Maximum number of posts to return
        
    Returns:
        List of latest BlogPost objects
    """
    try:
        posts = BlogPost.objects.filter(
            is_published=True
        ).order_by('-published_at')[:limit]
        
        logger.info(f"[BlogSearch] Retrieved {posts.count()} latest blog posts")
        return list(posts)
        
    except Exception as e:
        logger.error(f"[BlogSearch] Error fetching latest blog posts: {str(e)}")
        return []


def format_blog_post(post: BlogPost) -> str:
    """
    Format a blog post for chatbot response.
    
    Args:
        post: BlogPost object
        
    Returns:
        Formatted string representation of the blog post
    """
    # Truncate excerpt if too long
    excerpt = post.excerpt
    if len(excerpt) > 150:
        excerpt = excerpt[:147] + "..."
    
    # Format category and tags
    category = post.category.name if post.category else "General"
    tags = ", ".join([tag.name for tag in post.tags.all()[:3]]) if post.tags.exists() else ""
    
    formatted = (
        f"📝 {post.title}\n"
        f"📂 Category: {category}\n"
    )
    
    if tags:
        formatted += f"🏷️ Tags: {tags}\n"
    
    formatted += (
        f"📅 Published: {post.published_at.strftime('%B %d, %Y')}\n"
        f"👁️ Views: {post.views}\n\n"
        f"{excerpt}\n\n"
        f"🔗 Read more: /blog/{post.slug}\n"
    )
    
    return formatted


def format_blog_posts_list(posts: list) -> str:
    """
    Format multiple blog posts for chatbot response.
    
    Args:
        posts: List of BlogPost objects
        
    Returns:
        Formatted string with all blog posts
    """
    if not posts:
        return "No blog posts found matching your query."
    
    response = f"I found {len(posts)} blog post{'s' if len(posts) > 1 else ''}:\n\n"
    
    for i, post in enumerate(posts, 1):
        response += f"{i}. {format_blog_post(post)}\n"
    
    response += "\nWould you like to know more about any of these articles?"
    
    return response
