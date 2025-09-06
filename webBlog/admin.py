from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author')
        }),
        ('Markdown Help', {
            'fields': (),
            'description': """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h4>Markdown Formatting Guide:</h4>
                <ul>
                    <li><strong>Bold:</strong> **bold text**</li>
                    <li><strong>Italic:</strong> *italic text*</li>
                    <li><strong>Headers:</strong> # Header 1, ## Header 2, ### Header 3</li>
                    <li><strong>Links:</strong> [link text](https://example.com)</li>
                    <li><strong>Images:</strong> ![alt text](https://example.com/image.jpg)</li>
                    <li><strong>Lists:</strong> - item or 1. item</li>
                    <li><strong>Code:</strong> `inline code` or ```block code```</li>
                    <li><strong>Quote:</strong> > quoted text</li>
                </ul>
            </div>
            """
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'content_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'post__title')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'