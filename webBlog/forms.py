from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
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
            # Check for image markdown syntax
            if '![' in content and '](' in content:
                raise forms.ValidationError("Images are not allowed in comments.")
            # Check for link markdown syntax
            if '[' in content and '](' in content and not '![' in content:
                raise forms.ValidationError("Links are not allowed in comments.")
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


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
