import shutil
import tempfile


from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_test_forms')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another-test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария',
        )
        cls.form = PostForm()
        cls.url_create = reverse_lazy('posts:post_create')
        cls.url_create_redirect = reverse_lazy(
            'posts:profile',
            kwargs={'username': cls.user.username}
        )
        cls.url_edit = reverse_lazy('posts:post_edit',
                                    kwargs={'post_id': cls.post.pk})
        cls.url_edit_redirect = reverse_lazy('posts:post_detail',
                                             kwargs={'post_id': cls.post.pk})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        another_group = PostFormTests.another_group
        image = PostFormTests.uploaded
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Второй тестовый пост',
            'group': another_group.pk,
            'image': image,
        }
        response = self.authorized_client.post(
            PostFormTests.url_create,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.url_create_redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Второй тестовый пост',
                group=another_group
            ).exists()
        )

    def test_edit_post(self):
        post = PostFormTests.post
        another_group = PostFormTests.another_group
        form_data = {
            'text': 'Измененный текст',
            'group': another_group.pk,
        }
        response = self.authorized_client.post(
            PostFormTests.url_edit,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.url_edit_redirect)
        post = Post.objects.get(pk=post.pk)
        self.assertEqual(post.text, 'Измененный текст')
        self.assertEqual(post.group, another_group)

    def test_create_post_guest_access(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Неавторизованный клиент',
        }
        response = self.guest_client.post(
            PostFormTests.url_create,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(text='Неавторизованный клиент').exists()
        )

    def test_edit_post_guest_access(self):
        post = PostFormTests.post
        form_data = {
            'text': 'Неавторизованный клиент',
        }
        response = self.guest_client.post(
            PostFormTests.url_edit,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{post.pk}/edit/')
        post = Post.objects.get(pk=post.pk)
        self.assertNotEqual(post.text, 'Неавторизованный клиент')


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_test_form_comment')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария',
        )
        cls.form = CommentForm()
        cls.url_comment = reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.url_add_comment = reverse_lazy(
            'posts:add_comment',
            kwargs={'post_id': cls.post.pk}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentFormTests.user)

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Второй тестовый комментарий',
        }
        response = self.authorized_client.post(
            CommentFormTests.url_add_comment,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, CommentFormTests.url_comment)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Второй тестовый комментарий',
            ).exists()
        )

    def test_create_comment_guest_access(self):
        post = CommentFormTests.post
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Неавторизованный клиент',
        }
        response = self.guest_client.post(
            CommentFormTests.url_add_comment,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{post.pk}/comment/')
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(
            Post.objects.filter(text='Неавторизованный клиент').exists()
        )
