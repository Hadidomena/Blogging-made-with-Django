from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from .models import Post, Comment


@require_http_methods(["GET"])
def api_status(request):
    return JsonResponse({
        'status': 'active',
        'message': 'Simple Blog API is running',
        'version': '1.0',
        'authentication': 'Django Session Authentication',
        'endpoints': {
            'posts': {
                'list': '/api/posts/',
                'detail': '/api/posts/{id}/',
                'create': '/api/posts/create/',
            },
            'comments': {
                'list': '/api/posts/{post_id}/comments/',
                'create': '/api/posts/{post_id}/comments/create/',
            },
            'auth': {
                'status': '/api/auth/status/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'register': '/api/auth/register/',
            }
        }
    })


@require_http_methods(["GET"])
def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
            }
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'user': None
        })


@require_http_methods(["GET"])
def posts_list(request):
    sort_by = request.GET.get('sort', 'newest')
    
    if sort_by == 'oldest':
        posts = Post.objects.all().order_by('created_at')
    elif sort_by == 'updated_newest':
        posts = Post.objects.all().order_by('-updated_at')
    elif sort_by == 'updated_oldest':
        posts = Post.objects.all().order_by('updated_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    
    page_size = int(request.GET.get('page_size', 10))
    page_number = int(request.GET.get('page', 1))
    paginator = Paginator(posts, page_size)
    page = paginator.get_page(page_number)
    
    posts_data = []
    for post in page:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': post.author.username,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
            'comment_count': post.comments.count(),
        })
    
    return JsonResponse({
        'posts': posts_data,
        'pagination': {
            'current_page': page.number,
            'total_pages': paginator.num_pages,
            'total_posts': paginator.count,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
        },
        'sort': sort_by
    })


@require_http_methods(["GET"])
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    
    # Get comment sorting
    comment_sort = request.GET.get('comment_sort', 'oldest')
    if comment_sort == 'newest':
        comments = post.comments.all().order_by('-created_at')
    else:
        comments = post.comments.all().order_by('created_at')
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'is_approved': comment.is_approved,
        })
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
        'comments': comments_data,
        'comment_count': len(comments_data),
    }
    
    return JsonResponse(post_data)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_post(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or not content:
            return JsonResponse({'error': 'Title and content are required'}, status=400)
        
        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        
        return JsonResponse({
            'message': 'Post created successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'created_at': post.created_at.isoformat(),
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def post_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    
    # Get comment sorting
    comment_sort = request.GET.get('comment_sort', 'oldest')
    if comment_sort == 'newest':
        comments = post.comments.all().order_by('-created_at')
    else:
        comments = post.comments.all().order_by('created_at')
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'is_approved': comment.is_approved,
        })
    
    return JsonResponse({
        'post_id': post_id,
        'comments': comments_data,
        'comment_count': len(comments_data),
        'sort': comment_sort
    })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            is_approved=True
        )
        
        return JsonResponse({
            'message': 'Comment created successfully',
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return JsonResponse({'error': 'Username, email, and password are required'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return JsonResponse({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def api_logout(request):
    """Simple API logout"""
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'message': 'Logout successful'})