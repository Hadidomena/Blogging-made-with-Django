from django import template
from django.utils.safestring import mark_safe
import markdown
import re

register = template.Library()

@register.filter
def markdown_to_html(value):
    if not value:
        return ''
    
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
    
    html = md.convert(value)
    html = re.sub(r'<img ', r'<img class="markdown-image" ', html)
    html = re.sub(r'<a href="http', r'<a target="_blank" href="http', html)
    
    return mark_safe(html)

@register.filter
def markdown_to_html_safe(value):
    if not value:
        return ''
    
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.fenced_code',
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
    
    html = md.convert(value)
    html = re.sub(r'<img[^>]*>', '', html)
    html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html)
    html = re.sub(r'href="[^"]*"', '', html)
    
    return mark_safe(html)
