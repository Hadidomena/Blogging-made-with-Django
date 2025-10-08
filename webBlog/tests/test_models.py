from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from webBlog.models import Post, Comment


class PostModelTest(TestCase):
    """Test Post model business logic only"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a **test** post with markdown.',
            author=self.user
        )

    def test_post_comment_count(self):
        """Test custom comment_count method"""
        # Initially no comments
        self.assertEqual(self.post.comment_count(), 0)
        
        # Add an approved comment
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment',
            is_approved=True
        )
        self.assertEqual(self.post.comment_count(), 1)
        
        # Add an unapproved comment - this will also be counted by the current implementation
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Unapproved comment',
            is_approved=False
        )
        # Current implementation counts all comments, not just approved ones
        self.assertEqual(self.post.comment_count(), 2)

    def test_post_get_absolute_url(self):
        """Test custom get_absolute_url method"""
        expected_url = reverse('blog:post_detail', args=[self.post.pk])
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_get_sorted_comments(self):
        """Test the get_sorted_comments method with different sort orders"""
        # Create comments with different timestamps
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='First comment',
            is_approved=True
        )
        
        # Add slight delay to ensure different timestamps
        import time
        time.sleep(0.01)
        
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Second comment',
            is_approved=True
        )
        
        # Test oldest first (default)
        oldest_first = self.post.get_sorted_comments('oldest')
        self.assertEqual(list(oldest_first), [comment1, comment2])
        
        # Test newest first
        newest_first = self.post.get_sorted_comments('newest')
        self.assertEqual(list(newest_first), [comment2, comment1])
        
        # Test default behavior (should be oldest)
        default_sort = self.post.get_sorted_comments()
        self.assertEqual(list(default_sort), [comment1, comment2])


class CommentModelTest(TestCase):
    """Test Comment model business logic only"""
    
    def setUp(self):
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
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment with **markdown**',
            is_approved=True
        )

    def test_comment_get_absolute_url(self):
        """Test custom get_absolute_url method with anchor"""
        expected_url = f"{reverse('blog:post_detail', args=[self.post.pk])}#comment-{self.comment.id}"
        self.assertEqual(self.comment.get_absolute_url(), expected_url)

    def test_comment_approval_logic(self):
        """Test comment approval business logic"""
        # Test approved comment
        self.assertTrue(self.comment.is_approved)
        
        # Test unapproved comment
        unapproved_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Unapproved comment',
            is_approved=False
        )
        self.assertFalse(unapproved_comment.is_approved)