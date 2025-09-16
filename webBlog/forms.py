from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here... (Markdown supported: **bold**, *italic*, `code`, > quote)',
                'class': 'form-control',
                'maxlength': 1000
            })
        }
        labels = {
            'content': 'Your Comment (Markdown supported)'
        }
        help_texts = {
            'content': 'You can use: **bold**, *italic*, `code`, lists, and > quotes. Images and links are not allowed. Max 1000 characters.'
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            if len(content.strip()) < 3:
                raise forms.ValidationError("Comment must be at least 3 characters long.")
            if content.count('http') > 2:
                raise forms.ValidationError("Too many links in comment.")
        return content


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'autofocus' in self.fields['username'].widget.attrs:
            del self.fields['username'].widget.attrs['autofocus']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your post content here... (Markdown supported)'
            })
        }
        help_texts = {
            'content': 'Full Markdown support including images, links, code blocks, tables, etc.'
        }
