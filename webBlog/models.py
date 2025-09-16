from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(
        help_text="You can use Markdown formatting. For images: ![alt text](image_url)"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def comment_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    class Meta:
        ordering = ['created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"