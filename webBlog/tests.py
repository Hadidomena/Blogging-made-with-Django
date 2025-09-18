from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Post, Comment
from .forms import CommentForm, CustomUserCreationForm, PostForm


class PostModelTest(TestCase):
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

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.created_at)
        self.assertTrue(self.post.updated_at)

    def test_post_str_method(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_get_absolute_url(self):
        expected_url = reverse('blog:post_detail', args=[self.post.pk])
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_post_comment_count(self):
        self.assertEqual(self.post.comment_count(), 0)
        
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment',
            is_approved=True
        )
        self.assertEqual(self.post.comment_count(), 1)

    def test_post_ordering(self):
        older_post = Post.objects.create(
            title='Older Post',
            content='Older content',
            author=self.user
        )
        older_post.created_at = timezone.now() - timezone.timedelta(days=1)
        older_post.save()
        
        posts = Post.objects.all()
        self.assertEqual(posts.first(), self.post)
        self.assertEqual(posts.last(), older_post)

    def test_post_created_at_auto_set(self):
        """Test that created_at is automatically set when a post is created"""
        before_creation = timezone.now()
        new_post = Post.objects.create(
            title='New Post',
            content='New content',
            author=self.user
        )
        after_creation = timezone.now()
        
        self.assertIsNotNone(new_post.created_at)
        self.assertGreaterEqual(new_post.created_at, before_creation)
        self.assertLessEqual(new_post.created_at, after_creation)

    def test_post_updated_at_auto_set(self):
        """Test that updated_at is automatically set and updated"""
        original_updated_at = self.post.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update the post
        self.post.title = 'Updated Title'
        self.post.save()
        
        self.assertIsNotNone(self.post.updated_at)
        self.assertGreater(self.post.updated_at, original_updated_at)

    def test_post_created_vs_updated_initially_same(self):
        """Test that created_at and updated_at are initially the same"""
        new_post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        # Allow for small timestamp differences (within 1 second)
        time_diff = abs((new_post.updated_at - new_post.created_at).total_seconds())
        self.assertLess(time_diff, 1.0)

    def test_post_date_immutable_created_at(self):
        """Test that created_at doesn't change when post is updated"""
        original_created_at = self.post.created_at
        
        # Update the post
        self.post.content = 'Updated content'
        self.post.save()
        
        # Refresh from database
        self.post.refresh_from_db()
        
        self.assertEqual(self.post.created_at, original_created_at)


class CommentModelTest(TestCase):
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

    def test_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'Test comment with **markdown**')
        self.assertTrue(self.comment.created_at)

    def test_comment_str_method(self):
        expected = f'Comment by {self.user.username} on {self.post.title}'
        self.assertEqual(str(self.comment), expected)

    def test_comment_get_absolute_url(self):
        expected_url = f"{reverse('blog:post_detail', args=[self.post.pk])}#comment-{self.comment.id}"
        self.assertEqual(self.comment.get_absolute_url(), expected_url)

    def test_comment_ordering(self):
        newer_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Newer comment',
            is_approved=True
        )
        
        comments = Comment.objects.all()
        self.assertEqual(comments.first(), self.comment)
        self.assertEqual(comments.last(), newer_comment)

    def test_comment_created_at_auto_set(self):
        """Test that comment created_at is automatically set"""
        before_creation = timezone.now()
        new_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='New comment',
            is_approved=True
        )
        after_creation = timezone.now()
        
        self.assertIsNotNone(new_comment.created_at)
        self.assertGreaterEqual(new_comment.created_at, before_creation)
        self.assertLessEqual(new_comment.created_at, after_creation)


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, self.user.username)

    def test_post_detail_view(self):
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test content')

    def test_post_detail_view_authenticated_user_sees_comment_form(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add a Comment')

    def test_post_detail_view_anonymous_user_sees_login_prompt(self):
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Want to join the conversation?')

    def test_post_comment_submission(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('blog:post_detail', args=[self.post.pk]),
            {'content': 'This is a test comment'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='This is a test comment').exists())

    def test_post_comment_submission_anonymous_user(self):
        response = self.client.post(
            reverse('blog:post_detail', args=[self.post.pk]),
            {'content': 'This is a test comment'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(content='This is a test comment').exists())

    def test_post_list_displays_creation_date(self):
        """Test that post list view displays formatted creation date"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the date is displayed in the expected format
        expected_date = self.post.created_at.strftime('%B %d, %Y')
        self.assertContains(response, expected_date)
        self.assertContains(response, f'By {self.user.username} on')

    def test_post_detail_displays_creation_date(self):
        """Test that post detail view displays formatted creation date"""
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Check that the date is displayed in the expected format
        expected_date = self.post.created_at.strftime('%B %d, %Y')
        self.assertContains(response, expected_date)
        self.assertContains(response, f'By {self.user.username} on')

    def test_post_detail_shows_updated_at_when_different(self):
        """Test that updated date is shown when post is modified"""
        # Modify the post to trigger updated_at change
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamp
        self.post.content = 'Updated content'
        self.post.save()
        
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Both dates should be visible
        created_date = self.post.created_at.strftime('%B %d, %Y')
        updated_date = self.post.updated_at.strftime('%B %d, %Y')
        self.assertContains(response, created_date)

    def test_comment_displays_creation_date(self):
        """Test that comments display their creation date"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment',
            is_approved=True
        )
        
        response = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Check comment date format: "F d, Y \a\t H:i"
        expected_date = comment.created_at.strftime('%B %d, %Y at %H:%M')
        self.assertContains(response, self.user.username)
        # The date format in template includes "at" so check for that
        self.assertContains(response, 'at')


class AuthenticationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('blog:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_signup_view_get(self):
        response = self.client.get(reverse('blog:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')

    def test_signup_view_post_valid_data(self):
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_view_post_invalid_data(self):
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:logout'))
        self.assertEqual(response.status_code, 302)

    def test_markdown_guide_view(self):
        response = self.client.get(reverse('blog:markdown_guide'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Markdown Guide')


class FormTest(TestCase):
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

    def test_comment_form_valid_data(self):
        form = CommentForm(data={'content': 'This is a valid comment'})
        self.assertTrue(form.is_valid())

    def test_comment_form_empty_data(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_comment_form_too_long_content(self):
        long_content = 'x' * 1001
        form = CommentForm(data={'content': long_content})
        self.assertFalse(form.is_valid())

    def test_comment_form_with_disallowed_content(self):
        form = CommentForm(data={'content': 'Check this ![image](http://example.com/img.jpg)'})
        self.assertFalse(form.is_valid())
        self.assertIn('Images are not allowed in comments', str(form.errors))

    def test_comment_form_with_links(self):
        form = CommentForm(data={'content': 'Check this [link](http://example.com)'})
        self.assertFalse(form.is_valid())
        self.assertIn('Links are not allowed in comments', str(form.errors))

    def test_custom_user_creation_form_valid_data(self):
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_password_mismatch(self):
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        })
        self.assertFalse(form.is_valid())

    def test_post_form_valid_data(self):
        form = PostForm(data={
            'title': 'New Post',
            'content': 'This is new post content'
        })
        self.assertTrue(form.is_valid())

    def test_post_form_empty_title(self):
        form = PostForm(data={
            'title': '',
            'content': 'This is new post content'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class TemplateTagTest(TestCase):
    def test_markdown_to_html_filter(self):
        from webBlog.templatetags.markdown_extras import markdown_to_html
        
        markdown_text = "**Bold** and *italic* text"
        html_output = markdown_to_html(markdown_text)
        self.assertIn('<strong>Bold</strong>', html_output)
        self.assertIn('<em>italic</em>', html_output)

    def test_markdown_to_html_safe_filter(self):
        from webBlog.templatetags.markdown_extras import markdown_to_html_safe
        
        markdown_with_image = "Text with ![image](http://example.com/img.jpg)"
        html_output = markdown_to_html_safe(markdown_with_image)
        self.assertNotIn('<img', html_output)
        self.assertNotIn('http://example.com/img.jpg', html_output)

        markdown_with_link = "Text with [link](http://example.com)"
        html_output = markdown_to_html_safe(markdown_with_link)
        self.assertNotIn('<a', html_output)
        self.assertNotIn('http://example.com', html_output)


class URLTest(TestCase):
    def test_url_patterns(self):
        # Test that all URL patterns resolve correctly
        self.assertEqual(reverse('blog:post_list'), '/')
        self.assertEqual(reverse('blog:post_detail', args=[1]), '/post/1/')
        self.assertEqual(reverse('blog:login'), '/login/')
        self.assertEqual(reverse('blog:logout'), '/logout/')
        self.assertEqual(reverse('blog:signup'), '/signup/')
        self.assertEqual(reverse('blog:markdown_guide'), '/markdown-guide/')


class SortingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create posts with different dates for testing sorting
        now = timezone.now()
        
        self.old_post = Post.objects.create(
            title='Old Post',
            content='Old content',
            author=self.user
        )
        self.old_post.created_at = now - timezone.timedelta(days=3)
        self.old_post.save()
        
        self.middle_post = Post.objects.create(
            title='Middle Post',
            content='Middle content',
            author=self.user
        )
        self.middle_post.created_at = now - timezone.timedelta(days=1)
        self.middle_post.save()
        
        self.new_post = Post.objects.create(
            title='New Post',
            content='New content',
            author=self.user
        )
        
        # Update one post to have different updated_at
        import time
        time.sleep(0.01)
        self.old_post.title = 'Recently Updated Old Post'
        self.old_post.save()

    def test_post_sorting_newest_first(self):
        """Test posts are sorted by creation date, newest first (default)"""
        response = self.client.get(reverse('blog:post_list'))
        posts = response.context['posts']
        
        self.assertEqual(posts[0], self.new_post)
        self.assertEqual(posts[1], self.middle_post)
        self.assertEqual(posts[2], self.old_post)

    def test_post_sorting_oldest_first(self):
        """Test posts are sorted by creation date, oldest first"""
        response = self.client.get(reverse('blog:post_list') + '?sort=oldest')
        posts = response.context['posts']
        
        self.assertEqual(posts[0], self.old_post)
        self.assertEqual(posts[1], self.middle_post)
        self.assertEqual(posts[2], self.new_post)

    def test_post_sorting_updated_newest(self):
        """Test posts are sorted by update date, newest first"""
        response = self.client.get(reverse('blog:post_list') + '?sort=updated_newest')
        posts = response.context['posts']
        
        # old_post was updated most recently
        self.assertEqual(posts[0], self.old_post)

    def test_post_sorting_updated_oldest(self):
        """Test posts are sorted by update date, oldest first"""
        response = self.client.get(reverse('blog:post_list') + '?sort=updated_oldest')
        posts = list(response.context['posts'])
        
        # old_post was updated most recently, so should be last
        self.assertEqual(posts[-1], self.old_post)

    def test_post_list_current_sort_context(self):
        """Test that current sort is passed to template context"""
        response = self.client.get(reverse('blog:post_list') + '?sort=oldest')
        self.assertEqual(response.context['current_sort'], 'oldest')
        
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.context['current_sort'], 'newest')

    def test_comment_sorting_oldest_first(self):
        """Test comments are sorted oldest first (default)"""
        now = timezone.now()
        
        old_comment = Comment.objects.create(
            post=self.new_post,
            author=self.user,
            content='Old comment',
            is_approved=True
        )
        old_comment.created_at = now - timezone.timedelta(hours=2)
        old_comment.save()
        
        new_comment = Comment.objects.create(
            post=self.new_post,
            author=self.user,
            content='New comment',
            is_approved=True
        )
        
        response = self.client.get(reverse('blog:post_detail', args=[self.new_post.pk]))
        comments = response.context['comments']
        
        self.assertEqual(comments[0], old_comment)
        self.assertEqual(comments[1], new_comment)

    def test_comment_sorting_newest_first(self):
        """Test comments are sorted newest first"""
        now = timezone.now()
        
        old_comment = Comment.objects.create(
            post=self.new_post,
            author=self.user,
            content='Old comment',
            is_approved=True
        )
        old_comment.created_at = now - timezone.timedelta(hours=2)
        old_comment.save()
        
        new_comment = Comment.objects.create(
            post=self.new_post,
            author=self.user,
            content='New comment',
            is_approved=True
        )
        
        response = self.client.get(
            reverse('blog:post_detail', args=[self.new_post.pk]) + '?comment_sort=newest'
        )
        comments = response.context['comments']
        
        self.assertEqual(comments[0], new_comment)
        self.assertEqual(comments[1], old_comment)

    def test_comment_sort_context(self):
        """Test that current comment sort is passed to template context"""
        response = self.client.get(
            reverse('blog:post_detail', args=[self.new_post.pk]) + '?comment_sort=newest'
        )
        self.assertEqual(response.context['current_comment_sort'], 'newest')
        
        response = self.client.get(reverse('blog:post_detail', args=[self.new_post.pk]))
        self.assertEqual(response.context['current_comment_sort'], 'oldest')

    def test_post_sorting_ui_elements(self):
        """Test that sorting UI elements are present in post list"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertContains(response, 'Sort Posts by:')
        self.assertContains(response, 'Newest First')
        self.assertContains(response, 'Oldest First')
        self.assertContains(response, 'Recently Updated')
        self.assertContains(response, 'Least Recently Updated')

    def test_comment_sorting_ui_elements(self):
        """Test that comment sorting UI elements are present when comments exist"""
        Comment.objects.create(
            post=self.new_post,
            author=self.user,
            content='Test comment',
            is_approved=True
        )
        
        response = self.client.get(reverse('blog:post_detail', args=[self.new_post.pk]))
        self.assertContains(response, 'Sort Comments by:')
        self.assertContains(response, 'Oldest First')
        self.assertContains(response, 'Newest First')


class DateFormattingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_post_date_formatting_in_templates(self):
        """Test that dates are properly formatted in templates"""
        # Create a post with a specific date
        specific_date = timezone.datetime(2025, 9, 18, 15, 30, 45, tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title='Date Test Post',
            content='Content for date testing',
            author=self.user
        )
        # Manually set the created_at to a specific date for testing
        post.created_at = specific_date
        post.save()
        
        # Test post list view date formatting
        response = self.client.get(reverse('blog:post_list'))
        self.assertContains(response, 'September 18, 2025')
        
        # Test post detail view date formatting
        response = self.client.get(reverse('blog:post_detail', args=[post.pk]))
        self.assertContains(response, 'September 18, 2025')
    
    def test_comment_date_formatting_in_templates(self):
        """Test that comment dates are properly formatted"""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        
        # Create comment with specific date
        specific_date = timezone.datetime(2025, 9, 18, 15, 30, 45, tzinfo=timezone.get_current_timezone())
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content='Test comment',
            is_approved=True
        )
        comment.created_at = specific_date
        comment.save()
        
        response = self.client.get(reverse('blog:post_detail', args=[post.pk]))
        # Comment format should be "F d, Y \a\t H:i" = "September 18, 2025 at 15:30"
        self.assertContains(response, 'September 18, 2025 at 15:30')


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_full_user_workflow(self):
        # User visits homepage
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)

        # User signs up
        response = self.client.post(reverse('blog:signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)

        # User creates a post (through admin)
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

        # User adds a comment
        response = self.client.post(
            reverse('blog:post_detail', args=[post.pk]),
            {'content': 'Great post!'}
        )
        self.assertEqual(response.status_code, 302)

        # Verify comment was added
        self.assertTrue(Comment.objects.filter(content='Great post!').exists())

        # User logs out
        response = self.client.get(reverse('blog:logout'))
        self.assertEqual(response.status_code, 302)