from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here... (Markdown supported: **bold**, *italic*, `code`, > quote)',
                'class': 'form-control'
            })
        }
        labels = {
            'content': 'Your Comment (Markdown supported)'
        }
        help_texts = {
            'content': 'You can use: **bold**, *italic*, `code`, lists, and > quotes. Images and links are not allowed.'
        }
