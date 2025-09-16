from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Post, Comment
from .forms import PostForm


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'content', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostForm
    list_display = ('title', 'author', 'created_at', 'comment_count', 'view_on_site')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Markdown Help', {
            'fields': (),
            'description': mark_safe("""
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
            """)
        }),
    )
    
    def comment_count(self, obj):
        count = obj.comments.count()
        if count > 0:
            url = reverse('admin:webBlog_comment_changelist')
            return format_html(
                '<a href="{}?post__id__exact={}">{} comment{}</a>',
                url, obj.id, count, 's' if count != 1 else ''
            )
        return "0 comments"
    comment_count.short_description = "Comments"
    
    def view_on_site(self, obj):
        url = reverse('blog:post_detail', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">View on site</a>', url)
    view_on_site.short_description = "View"
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_link', 'author', 'created_at', 'content_preview', 'view_on_site')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('content', 'post__title', 'author__username')
    readonly_fields = ('created_at', 'post', 'author')
    
    def post_link(self, obj):
        url = reverse('admin:webBlog_post_change', args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_link.short_description = "Post"
    
    def content_preview(self, obj):
        content = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, content)
    content_preview.short_description = 'Content Preview'
    
    def view_on_site(self, obj):
        url = reverse('blog:post_detail', args=[obj.post.pk])
        return format_html('<a href="{}#comment-{}" target="_blank">View on site</a>', url, obj.id)
    view_on_site.short_description = "View"
    
    def has_add_permission(self, request):
        return False