from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from posts.models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):

    NUM_POST_ONE_PAGE = 10
    NUM_POST_TWO_PAGE = 7

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_test_views')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([Post(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )] * (cls.NUM_POST_ONE_PAGE + cls.NUM_POST_TWO_PAGE))
        cls.url_index = reverse_lazy('posts:index')
        cls.url_group_posts = reverse_lazy('posts:group_posts',
                                           kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse_lazy('posts:profile',
                                       kwargs={'username': cls.user.username})
        cls.urls = [cls.url_index, cls.url_group_posts, cls.url_profile]

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_records(self):
        for url in PaginatorViewsTest.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 self.NUM_POST_ONE_PAGE)

    def test_second_page_contains_records(self):
        for url in PaginatorViewsTest.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.NUM_POST_TWO_PAGE)
