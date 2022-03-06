from django.test import TestCase, Client

from http import HTTPStatus


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_signup = '/auth/signup/'
        cls.url_no_exist = '/auth/no_existing_page/'
        cls.urls = {
            cls.url_signup: 'users/signup.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_posts_urls_guest_access_exists_at_desired_location_and_templates(
            self):
        for url, template in UsersURLTests.urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_no_existing_page_404_error(self):
        response = self.guest_client.get(UsersURLTests.url_no_exist)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
