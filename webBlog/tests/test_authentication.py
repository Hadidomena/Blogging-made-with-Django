from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from webBlog.forms import CommentForm, CustomUserCreationForm, PostForm


class AuthenticationViewTest(TestCase):
    """Test authentication workflows and business logic"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_with_valid_credentials(self):
        """Test successful login flow"""
        response = self.client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        """Test failed login shows error message"""
        response = self.client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_signup_creates_new_user(self):
        """Test successful user registration"""
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_with_invalid_data_fails(self):
        """Test that invalid signup data doesn't create user"""
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_logout_redirects(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:logout'))
        self.assertEqual(response.status_code, 302)


class FormValidationTest(TestCase):
    """Test custom form validation logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_comment_form_validates_content_length(self):
        """Test comment form enforces content length limits"""
        # Valid comment
        form = CommentForm(data={'content': 'This is a valid comment'})
        self.assertTrue(form.is_valid())
        
        # Too long comment
        long_content = 'x' * 1001
        form = CommentForm(data={'content': long_content})
        self.assertFalse(form.is_valid())

    def test_comment_form_blocks_images_and_links(self):
        """Test custom validation that blocks images and links in comments"""
        # Test image blocking
        form = CommentForm(data={'content': 'Check this ![image](http://example.com/img.jpg)'})
        self.assertFalse(form.is_valid())
        self.assertIn('Images are not allowed in comments', str(form.errors))
        
        # Test link blocking
        form = CommentForm(data={'content': 'Check this [link](http://example.com)'})
        self.assertFalse(form.is_valid())
        self.assertIn('Links are not allowed in comments', str(form.errors))

    def test_comment_form_requires_content(self):
        """Test that comment form requires content"""
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_custom_user_creation_form_requires_matching_passwords(self):
        """Test custom user form validates password confirmation"""
        # Valid form
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertTrue(form.is_valid())
        
        # Password mismatch
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        })
        self.assertFalse(form.is_valid())

    def test_post_form_requires_title(self):
        """Test that post form requires a title"""
        # Valid form
        form = PostForm(data={
            'title': 'New Post',
            'content': 'This is new post content'
        })
        self.assertTrue(form.is_valid())
        
        # Empty title
        form = PostForm(data={
            'title': '',
            'content': 'This is new post content'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)