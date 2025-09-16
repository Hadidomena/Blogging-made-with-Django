from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import CommentForm, CustomAuthenticationForm


class PostListView(ListView):
    model = Post
    template_name = 'webBlog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']


class PostDetailView(DetailView):
    model = Post
    template_name = 'webBlog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('created_at')
        context['form'] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in to comment.')
            return redirect('blog:login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class MarkdownGuideView(TemplateView):
    template_name = 'webBlog/markdown_guide.html'


class CustomLoginView(LoginView):
    template_name = 'webBlog/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return reverse_lazy('blog:post_list')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = 'blog:post_list'
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'You have been logged out.')
        return response
