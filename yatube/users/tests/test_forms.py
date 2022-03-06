from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_create = reverse_lazy('users:signup')
        cls.url_create_redirect = reverse_lazy('posts:index')

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'test_user',
            'password1': 'hgfjhfijhh87832jkjk',
            'password2': 'hgfjhfijhh87832jkjk',
        }
        response = self.guest_client.post(
            PostFormTests.url_create,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.url_create_redirect)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username='test_user').exists()
        )
