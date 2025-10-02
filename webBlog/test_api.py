import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content for the post',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            content='Test comment',
            author=self.user
        )

    def test_api_status(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'active')
        self.assertIn('endpoints', data)

    def test_auth_status_anonymous(self):
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['authenticated'])
        self.assertIsNone(data['user'])

    def test_auth_status_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['user']['username'], 'testuser')

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/auth/register/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'User created successfully')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_duplicate_username(self):
        data = {
            'username': 'testuser',  # Already exists
            'email': 'another@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/auth/register/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('Username already exists', response_data['error'])

    def test_user_login_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Login successful')
        self.assertEqual(response_data['user']['username'], 'testuser')

    def test_user_login_invalid(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn('Invalid credentials', response_data['error'])

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Logout successful')

    def test_posts_list(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('posts', data)
        self.assertIn('pagination', data)
        self.assertEqual(len(data['posts']), 1)
        self.assertEqual(data['posts'][0]['title'], 'Test Post')

    def test_posts_list_sorting(self):
        # Create another post
        Post.objects.create(
            title='Newer Post',
            content='Newer content',
            author=self.user
        )
        
        # Test newest first (default)
        response = self.client.get('/api/posts/?sort=newest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['posts'][0]['title'], 'Newer Post')
        
        # Test oldest first
        response = self.client.get('/api/posts/?sort=oldest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['posts'][0]['title'], 'Test Post')

    def test_posts_list_pagination(self):
        # Create multiple posts
        for i in range(15):
            Post.objects.create(
                title=f'Post {i}',
                content=f'Content {i}',
                author=self.user
            )
        
        response = self.client.get('/api/posts/?page_size=5&page=1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['posts']), 5)
        self.assertEqual(data['pagination']['current_page'], 1)
        self.assertTrue(data['pagination']['has_next'])

    def test_post_detail(self):
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['author'], 'testuser')
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['content'], 'Test comment')

    def test_post_detail_not_found(self):
        response = self.client.get('/api/posts/999/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('Post not found', data['error'])

    def test_post_comments(self):
        response = self.client.get(f'/api/posts/{self.post.id}/comments/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['post_id'], self.post.id)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['content'], 'Test comment')

    def test_post_comments_sorting(self):
        # Create another comment
        Comment.objects.create(
            post=self.post,
            content='Newer comment',
            author=self.user
        )
        
        # Test oldest first (default)
        response = self.client.get(f'/api/posts/{self.post.id}/comments/?comment_sort=oldest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['comments'][0]['content'], 'Test comment')
        
        # Test newest first
        response = self.client.get(f'/api/posts/{self.post.id}/comments/?comment_sort=newest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['comments'][0]['content'], 'Newer comment')

    def test_create_post_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'New API Post',
            'content': 'Content created via API'
        }
        response = self.client.post('/api/posts/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Post created successfully')
        self.assertEqual(response_data['post']['title'], 'New API Post')
        self.assertTrue(Post.objects.filter(title='New API Post').exists())

    def test_create_post_unauthenticated(self):
        data = {
            'title': 'New API Post',
            'content': 'Content created via API'
        }
        response = self.client.post('/api/posts/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_post_missing_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': '',  # Empty title
            'content': 'Content created via API'
        }
        response = self.client.post('/api/posts/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('Title and content are required', response_data['error'])

    def test_create_comment_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'content': 'New comment via API'
        }
        response = self.client.post(f'/api/posts/{self.post.id}/comments/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Comment created successfully')
        self.assertEqual(response_data['comment']['content'], 'New comment via API')
        self.assertTrue(Comment.objects.filter(content='New comment via API').exists())

    def test_create_comment_unauthenticated(self):
        """Test creating comment when not authenticated"""
        data = {
            'content': 'New comment via API'
        }
        response = self.client.post(f'/api/posts/{self.post.id}/comments/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_comment_missing_content(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'content': ''  # Empty content
        }
        response = self.client.post(f'/api/posts/{self.post.id}/comments/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('Content is required', response_data['error'])

    def test_create_comment_invalid_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'content': 'Comment for non-existent post'
        }
        response = self.client.post('/api/posts/999/comments/create/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn('Post not found', response_data['error'])

    def test_invalid_json_data(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Test with invalid JSON
        response = self.client.post('/api/posts/create/', 
                                  'invalid json', 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('Invalid JSON', response_data['error'])

    def test_api_error_handling(self):
        # Test missing required fields in registration
        data = {
            'username': '',
            'email': '',
            'password': ''
        }
        response = self.client.post('/api/auth/register/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test missing required fields in login
        data = {
            'username': '',
            'password': ''
        }
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)


class APIIntegrationTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()

    def test_complete_user_workflow(self):
        # 1. Register new user
        register_data = {
            'username': 'workflowuser',
            'email': 'workflow@example.com',
            'password': 'workflow123'
        }
        response = self.client.post('/api/auth/register/', 
                                  json.dumps(register_data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'User created successfully')
        
        # 2. Login with new user
        login_data = {
            'username': 'workflowuser',
            'password': 'workflow123'
        }
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(login_data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Login successful')
        
        # 3. Check auth status
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['authenticated'])
        
        # 4. Create a post
        post_data = {
            'title': 'Workflow Test Post',
            'content': 'This post was created through the complete workflow'
        }
        response = self.client.post('/api/posts/create/', 
                                  json.dumps(post_data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        post_id = response.json()['post']['id']
        
        # 5. Add a comment to the post
        comment_data = {
            'content': 'This is a workflow test comment'
        }
        response = self.client.post(f'/api/posts/{post_id}/comments/create/', 
                                  json.dumps(comment_data), 
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Comment created successfully')
        
        # 6. Verify the post appears in the list
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['posts']), 1)
        self.assertEqual(data['posts'][0]['title'], 'Workflow Test Post')
        
        # 7. Verify post detail includes the comment
        response = self.client.get(f'/api/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['content'], 'This is a workflow test comment')
        
        # 8. Logout
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Logout successful')
        
        # 9. Verify no longer authenticated
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['authenticated'])

    def test_api_pagination_workflow(self):
        # Create user and login
        user = User.objects.create_user(
            username='paginationuser',
            password='test123'
        )
        self.client.login(username='paginationuser', password='test123')
        
        # Create multiple posts
        for i in range(25):
            Post.objects.create(
                title=f'Pagination Test Post {i}',
                content=f'Content for post {i}',
                author=user
            )
        
        # Test first page
        response = self.client.get('/api/posts/?page_size=10&page=1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['posts']), 10)
        self.assertEqual(data['pagination']['current_page'], 1)
        self.assertEqual(data['pagination']['total_pages'], 3)
        self.assertTrue(data['pagination']['has_next'])
        self.assertFalse(data['pagination']['has_previous'])
        
        # Test second page
        response = self.client.get('/api/posts/?page_size=10&page=2')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['posts']), 10)
        self.assertEqual(data['pagination']['current_page'], 2)
        self.assertTrue(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])
        
        # Test last page
        response = self.client.get('/api/posts/?page_size=10&page=3')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['posts']), 5)
        self.assertEqual(data['pagination']['current_page'], 3)
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])