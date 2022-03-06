from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
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

    def test_models_have_correct_object_names(self):

        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment

        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

        expected_object_name = comment.text[:10]
        self.assertEqual(expected_object_name, str(comment))

    def test_verbose_name(self):

        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment

        field_verboses = {
            post: {
                'text': 'Текст записи',
                'created': 'Дата и время публикации',
                'author': 'Автор',
                'group': 'Группа записей',
            },
            group: {
                'title': 'Название группы',
                'slug': 'Адрес группы',
                'description': 'Описание',
            },
            comment: {
                'post': 'Запись',
                'author': 'Автор',
                'text': 'Текст комментария',
                'created': 'Дата и время публикации',
            },
        }
        for model in field_verboses:
            for field, expected_value in field_verboses[model].items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value
                    )

    def test_help_text(self):

        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment

        field_help_texts = {
            post: {
                'text': 'Введите текст записи',
                'created': 'Автоматически задается при публикации',
                'author': 'Автор записи',
                'group': 'Привязка к конкретной группе записей',
            },
            group: {
                'title': 'Максимальная длина названия 200 символов.',
                'slug': 'Уникальный адрес группы, часть URL (например, '
                        'для группы любителей котиков slug будет равен '
                        'cats: group/cats).',
                'description': 'Текст, описывающий сообщество. Этот текст '
                               'будет отображаться на странице сообщества.',
            },
            comment: {
                'post': 'Запись, к которой относится комментарий',
                'author': 'Автор комментария',
                'text': 'Введите текст комментария к записи',
                'created': 'Автоматически задается при публикации',
            },
        }
        for model in field_help_texts:
            for field, expected_value in field_help_texts[model].items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_value
                    )
