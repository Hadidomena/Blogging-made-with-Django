from django.urls import path
from . import simple_api_views

app_name = 'api'

urlpatterns = [
    path('', simple_api_views.api_status, name='api_status'),
    path('posts/', simple_api_views.posts_list, name='posts_list'),
    path('posts/<int:post_id>/', simple_api_views.post_detail, name='post_detail'),
    path('posts/create/', simple_api_views.create_post, name='create_post'),
    path('posts/<int:post_id>/comments/', simple_api_views.post_comments, name='post_comments'),
    path('posts/<int:post_id>/comments/create/', simple_api_views.create_comment, name='create_comment'),
    path('auth/status/', simple_api_views.auth_status, name='auth_status'),
    path('auth/login/', simple_api_views.api_login, name='api_login'),
    path('auth/register/', simple_api_views.api_register, name='api_register'),
    path('auth/logout/', simple_api_views.api_logout, name='api_logout'),
]