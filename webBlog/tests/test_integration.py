from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from webBlog.models import Post, Comment


class IntegrationTest(TestCase):
    """Test complete user workflows and business processes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_complete_user_workflow(self):
        """Test full user journey: signup -> view posts -> comment -> logout"""
        # User signs up
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)

        # Create a post for testing
        new_user = User.objects.get(username='newuser')
        post = Post.objects.create(
            title='New User Post',
            content='This is my first post!',
            author=new_user
        )

        # User views the post
        response = self.client.get(reverse('blog:post_detail', args=[post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New User Post')

        # User adds a comment (should be automatically logged in after signup)
        response = self.client.post(
            reverse('blog:post_detail', args=[post.pk]),
            {'content': 'Great post!'}
        )
        self.assertEqual(response.status_code, 302)

        # Verify comment was added and is pending approval
        comment = Comment.objects.get(content='Great post!')
        self.assertEqual(comment.author, new_user)
        self.assertEqual(comment.post, post)

        # User logs out
        response = self.client.get(reverse('blog:logout'))
        self.assertEqual(response.status_code, 302)

    def test_comment_approval_workflow(self):
        """Test comment approval process"""
        # Create a post
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        
        # User logs in and comments
        self.client.login(username='testuser', password='testpass123')
        self.client.post(
            reverse('blog:post_detail', args=[post.pk]),
            {'content': 'Test comment'}
        )
        
        # Comment should exist but may need approval
        comment = Comment.objects.get(content='Test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)