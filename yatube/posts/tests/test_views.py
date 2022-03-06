import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse_lazy
from django.core.cache import cache
from posts.models import Post, Group, Comment, Follow
from django import forms

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_test_views')
        cls.another_user = User.objects.create_user(
            username='user_test_follow')
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
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария',
        )
        cls.url_index = reverse_lazy('posts:index')
        cls.url_group_posts = reverse_lazy('posts:group_posts',
                                           kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse_lazy('posts:profile',
                                       kwargs={'username': cls.user.username})
        cls.url_post_detail = reverse_lazy('posts:post_detail',
                                           kwargs={'post_id': cls.post.pk})
        cls.url_post_create = reverse_lazy('posts:post_create')
        cls.url_post_edit = reverse_lazy('posts:post_edit',
                                         kwargs={'post_id': cls.post.pk})
        cls.url_another_group_post = reverse_lazy(
            'posts:group_posts',
            kwargs={'slug': cls.another_group.slug}
        )
        cls.url_follow = reverse_lazy('posts:follow_index')
        cls.url_follow_add = reverse_lazy(
            'posts:profile_follow',
            kwargs={'username': cls.user.username}
        )
        cls.url_follow_del = reverse_lazy(
            'posts:profile_unfollow',
            kwargs={'username': cls.user.username}
        )
        cls.urls = {
            cls.url_index: 'posts/index.html',
            cls.url_group_posts: 'posts/group_list.html',
            cls.url_profile: 'posts/profile.html',
            cls.url_post_detail: 'posts/post_detail.html',
            cls.url_post_create: 'posts/post_create.html',
            cls.url_post_edit: 'posts/post_create.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client_follow = Client()
        self.authorized_client_follow.force_login(PostPagesTests.another_user)

    def test_pages_users_correct_template(self):
        for reverse_name, template in PostPagesTests.urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_posts_show_correct_context_page_obj(self):
        post = PostPagesTests.post
        urls_context_page_obj = [
            PostPagesTests.url_index,
            PostPagesTests.url_group_posts,
            PostPagesTests.url_profile
        ]
        for url in urls_context_page_obj:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, post.text)
                self.assertEqual(first_object.author, post.author)
                self.assertEqual(first_object.group, post.group)
                self.assertEqual(first_object.created, post.created)
                self.assertEqual(first_object.image, post.image)

    def test_group_posts_show_correct_context(self):
        author = PostPagesTests.user
        group = PostPagesTests.group
        another_group = PostPagesTests.another_group
        Post.objects.create(text='text', author=author, group=another_group)
        url = PostPagesTests.url_group_posts
        response = self.guest_client.get(url)
        for obj in response.context['page_obj']:
            self.assertEqual(obj.group, group)

    def test_profile_show_correct_context(self):
        author = PostPagesTests.user
        another_author = User.objects.create_user(username='another_author')
        Post.objects.create(text='text', author=another_author)
        url = PostPagesTests.url_profile
        response = self.guest_client.get(url)
        for obj in response.context['page_obj']:
            self.assertEqual(obj.author, author)
        self.assertEqual(response.context.get('posts_count'), 1)

    def test_post_detail_show_correct_context(self):
        url = PostPagesTests.url_post_detail
        response = self.guest_client.get(url)
        post = PostPagesTests.post
        self.assertEqual(response.context.get('post').id, post.id)
        self.assertEqual(response.context.get('post').image, post.image)
        self.assertEqual(response.context.get('post').comments, post.comments)
        self.assertEqual(response.context.get('posts_count'), 1)

    def test_posts_form_fields_correct_type(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        urls_form_fields = [PostPagesTests.url_post_create,
                            PostPagesTests.url_post_edit]
        for url in urls_form_fields:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_comment_form_fields_correct_type(self):
        form_fields = {
            'text': forms.fields.CharField,
        }
        url = PostPagesTests.url_post_detail
        response = self.authorized_client.get(url)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_with_group(self):
        post = PostPagesTests.post
        urls = [PostPagesTests.url_index, PostPagesTests.url_group_posts,
                PostPagesTests.url_profile]
        urls_another_group = PostPagesTests.url_another_group_post
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn(post, response.context['page_obj'])
        response = self.authorized_client.get(urls_another_group)
        self.assertNotIn(post, response.context['page_obj'])

    def test_index_cache(self):
        another_post = Post.objects.create(
            author=PostPagesTests.user,
            text='Тестовая пост для тестирования кэша',
            group=PostPagesTests.group,
        )
        content_after = (self.authorized_client
                         .get(PostPagesTests.url_index).content)
        another_post.delete()
        content_before = (self.authorized_client
                          .get(PostPagesTests.url_index).content)
        self.assertEqual(content_after, content_before)
        cache.clear()
        content_before_clear = (self.authorized_client
                                .get(PostPagesTests.url_index).content)
        self.assertNotEqual(content_after, content_before_clear)

    def test_auth_user_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client_follow.get(PostPagesTests.url_follow_add)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.authorized_client_follow.get(PostPagesTests.url_follow_del)
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_new_post_add_list_follow(self):
        post = PostPagesTests.post
        self.authorized_client_follow.get(PostPagesTests.url_follow_add)
        response = self.authorized_client_follow.get(PostPagesTests.url_follow)
        self.assertIn(post, response.context['page_obj'])
        response = self.authorized_client.get(PostPagesTests.url_follow)
        self.assertNotIn(post, response.context['page_obj'])
