from django import template
from django.utils.safestring import mark_safe
import markdown
import re

register = template.Library()

@register.filter
def markdown_to_html(value):
    """
    Convert markdown text to HTML with support for images and basic formatting
    """
    if not value:
        return ''
    
    # Configure markdown with extensions
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.codehilite',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': False,
            }
        }
    )
    
    # Convert markdown to HTML
    html = md.convert(value)
    
    # Add some basic styling classes to images
    html = re.sub(r'<img ', r'<img class="markdown-image" ', html)
    
    # Make external links open in new tab
    html = re.sub(r'<a href="http', r'<a target="_blank" href="http', html)
    
    return mark_safe(html)
