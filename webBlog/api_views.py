from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Post, Comment
from .serializers import (
    PostSerializer, PostListSerializer, CommentSerializer, 
    UserSerializer, UserRegistrationSerializer
)


# User Views
class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create a new post"""
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Post.objects.annotate(comment_count=Count('comments'))
        
        # Handle sorting
        sort_by = self.request.query_params.get('sort', 'newest')
        if sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'updated_newest':
            queryset = queryset.order_by('-updated_at')
        elif sort_by == 'updated_oldest':
            queryset = queryset.order_by('updated_at')
        else:  # default to 'newest'
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostSerializer
        return PostListSerializer


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific post"""
    queryset = Post.objects.annotate(comment_count=Count('comments'))
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        """Only allow authors to edit/delete their posts"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    """List comments for a post or create a new comment"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(id=post_id)
        
        # Handle comment sorting using model method
        comment_sort = self.request.query_params.get('comment_sort', 'oldest')
        return post.get_sorted_comments(comment_sort).filter(post_id=post_id)
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(author=self.request.user, post_id=post_id)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        """Only allow authors to edit/delete their comments"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]


# User Views
class UserProfileView(generics.RetrieveAPIView):
    """Get user profile"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserPostsView(generics.ListAPIView):
    """List posts by a specific user"""
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(author_id=user_id).annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')


# Custom Permission Class
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the author
        return obj.author == request.user


# API Status View
@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """API status endpoint"""
    return Response({
        'status': 'active',
        'message': 'Blog API is running',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/',
                'login': '/api/auth/api/',  # DRF browsable API login
            },
            'posts': {
                'list_create': '/api/posts/',
                'detail': '/api/posts/{id}/',
                'user_posts': '/api/users/{user_id}/posts/',
            },
            'comments': {
                'list_create': '/api/posts/{post_id}/comments/',
                'detail': '/api/comments/{id}/',
            },
            'user': {
                'profile': '/api/user/profile/',
            }
        }
    })