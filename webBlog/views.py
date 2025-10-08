from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from .models import Post, Comment
from .forms import CommentForm, CustomAuthenticationForm, CustomUserCreationForm


class PostListView(ListView):
    model = Post
    template_name = 'webBlog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get('sort', 'newest')
        
        if sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'updated_newest':
            queryset = queryset.order_by('-updated_at')
        elif sort_by == 'updated_oldest':
            queryset = queryset.order_by('updated_at')
        else:  # default to 'newest'
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'webBlog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Handle comment sorting
        comment_sort = self.request.GET.get('comment_sort', 'oldest')
        comments = self.object.get_sorted_comments(comment_sort)
            
        context['comments'] = comments
        context['current_comment_sort'] = comment_sort
        
        if self.request.user.is_authenticated:
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
    http_method_names = ['get', 'post']
    
    def get(self, request, *args, **kwargs):
        # For GET requests, perform logout and redirect
        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out.')
            logout(request)
        return redirect('blog:post_list')
    
    def post(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out.')
        return super().post(request, *args, **kwargs)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'webBlog/signup.html'
    success_url = reverse_lazy('blog:post_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blog:post_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome to the blog, {self.object.username}! Your account has been created.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
