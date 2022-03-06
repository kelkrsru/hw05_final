from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from django import forms

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_signup = reverse_lazy('users:signup')

    def setUp(self):
        self.guest_client = Client()

    def test_pages_users_correct_template(self):
        template = 'users/signup.html'
        response = self.guest_client.get(UsersPagesTests.url_signup)
        self.assertTemplateUsed(response, template)

    def test_signup_page_correct_context(self):
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        response = self.guest_client.get(UsersPagesTests.url_signup)
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
