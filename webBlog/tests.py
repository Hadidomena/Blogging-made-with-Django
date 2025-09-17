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
            content='Test comment'
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
            content='Test comment with **markdown**'
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
        expected_url = reverse('blog:post_detail', args=[self.post.pk])
        self.assertEqual(self.comment.get_absolute_url(), expected_url)

    def test_comment_ordering(self):
        newer_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Newer comment'
        )
        
        comments = Comment.objects.all()
        self.assertEqual(comments.first(), self.comment)
        self.assertEqual(comments.last(), newer_comment)


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
        self.assertContains(response, 'Please enter a correct username and password')

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