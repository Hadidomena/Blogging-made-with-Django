from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Post, Comment
from .forms import CommentForm

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'webBlog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Your comment has been added!')
                return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'You need to be logged in to comment.')
            return redirect('login')
    else:
        form = CommentForm()
    
    return render(request, 'webBlog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def markdown_guide(request):
    return render(request, 'webBlog/markdown_guide.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('post_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'webBlog/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('post_list')
