from django.test import TestCase, Client

from http import HTTPStatus


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_author = '/about/author/'
        cls.url_tech = '/about/tech/'
        cls.url_no_exist = '/about/no_existing_page/'
        cls.urls = {
            cls.url_author: 'about/author.html',
            cls.url_tech: 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_posts_urls_guest_access_exists_at_desired_location_and_templates(
            self):
        for url, template in AboutURLTests.urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_no_existing_page_404_error(self):
        response = self.guest_client.get(AboutURLTests.url_no_exist)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
