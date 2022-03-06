from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_test_urls')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

        cls.url_index = '/'
        cls.url_group_posts = f'/group/{cls.group.slug}/'
        cls.url_profile = f'/profile/{cls.user.username}/'
        cls.url_post_detail = f'/posts/{cls.post.pk}/'
        cls.url_post_create = '/create/'
        cls.url_post_edit = f'/posts/{cls.post.pk}/edit/'
        cls.url_post_no_exist = '/posts/100500/'
        cls.url_no_exist = '/posts/no_existing_page/'
        cls.url_comment = f'/posts/{cls.post.pk}/comment/'

        cls.urls = {
            'anonymous': {
                cls.url_index: 'posts/index.html',
                cls.url_group_posts: 'posts/group_list.html',
                cls.url_profile: 'posts/profile.html',
                cls.url_post_detail: 'posts/post_detail.html',
            },
            'auth': {
                cls.url_post_create: 'posts/post_create.html',
                cls.url_post_edit: 'posts/post_create.html',
            },
        }

        cls.urls_redirect = {
            cls.url_post_create: '/auth/login/?next=/create/',
            cls.url_post_edit: f'/auth/login/?next=/posts/{cls.post.pk}/edit/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_posts_urls_guest_access_exists_at_desired_location_and_templates(
            self):
        for url, template in PostURLTests.urls['anonymous'].items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_auth_access_exists_at_desired_location_and_templates(
            self):
        for url, template in PostURLTests.urls['auth'].items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_redirect_anonymous(self):
        for url, url_redirect in PostURLTests.urls_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_comment_url_redirect(self):
        url = PostURLTests.url_comment
        url_redirect = PostURLTests.url_post_detail
        response = self.authorized_client.get(url, follow=True)
        self.assertRedirects(response, url_redirect)

    def test_post_edit_no_author_access_redirect(self):
        another_user = User.objects.create_user(username='another_user')
        authorized_client_another_user = Client()
        authorized_client_another_user.force_login(another_user)
        response = authorized_client_another_user.get(
            PostURLTests.url_post_edit, follow=True)
        self.assertRedirects(
            response, PostURLTests.url_post_detail
        )

    def test_no_existing_post_404_error(self):
        response = self.guest_client.get(PostURLTests.url_post_no_exist)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_no_existing_page_404_error(self):
        response = self.guest_client.get(PostURLTests.url_no_exist)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
