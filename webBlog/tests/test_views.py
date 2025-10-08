from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from webBlog.models import Post, Comment


class PostViewTest(TestCase):
    """Test Post view business logic and authentication requirements"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )

    def test_post_list_view_displays_posts(self):
        """Test that post list view displays posts correctly"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, self.user.username)

    def test_post_detail_view_displays_content(self):
        """Test that post detail view displays post content"""
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test content')

    def test_authenticated_user_sees_comment_form(self):
        """Test that logged-in users can see comment form"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add a Comment')

    def test_anonymous_user_sees_login_prompt(self):
        """Test that anonymous users see login prompt instead of comment form"""
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Want to join the conversation?')

    def test_authenticated_user_can_submit_comment(self):
        """Test that authenticated users can submit comments"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('blog:post_detail', args=[self.post.pk]),
            {'content': 'This is a test comment'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        self.assertTrue(Comment.objects.filter(content='This is a test comment').exists())

    def test_anonymous_user_cannot_submit_comment(self):
        """Test that anonymous users cannot submit comments"""
        response = self.client.post(
            reverse('blog:post_detail', args=[self.post.pk]),
            {'content': 'This is a test comment'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(Comment.objects.filter(content='This is a test comment').exists())

    def test_all_comments_display_current_behavior(self):
        """Test current behavior - displays ALL comments (both approved and unapproved)
        
        Note: This might be a bug - typically only approved comments should be shown.
        TODO: Consider filtering comments by is_approved=True in the view.
        """
        # Create approved comment
        approved_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Approved comment',
            is_approved=True
        )
        
        # Create unapproved comment
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Unapproved comment',
            is_approved=False
        )
        
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Current behavior: both comments are displayed
        self.assertContains(response, 'Approved comment')
        self.assertContains(response, 'Unapproved comment')  # This might be unexpected behavior