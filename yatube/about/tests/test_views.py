from django.urls import reverse_lazy
from django.test import TestCase, Client

from http import HTTPStatus


class AboutPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_author = reverse_lazy('about:author')
        cls.url_tech = reverse_lazy('about:tech')
        cls.urls = {
            cls.url_author: 'about/author.html',
            cls.url_tech: 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_pages_users_correct_template(self):
        for reverse_name, template in AboutPagesTests.urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
