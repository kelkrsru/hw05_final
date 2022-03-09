from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации',
        help_text='Автоматически задается при публикации',
    )

    class Meta:
        abstract = True


class Post(CreatedModel):
    """Модель записи"""

    text = models.TextField(
        verbose_name='Текст записи',
        help_text='Введите текст записи',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author_posts',
        help_text='Автор записи',
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа записей',
        help_text='Привязка к конкретной группе записей',
        on_delete=models.SET_NULL,
        related_name='group_posts',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    """Модель группы для записей"""

    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Максимальная длина названия 200 символов.',
    )
    slug = models.SlugField(
        verbose_name='Адрес группы',
        help_text='Уникальный адрес группы, часть URL (например, для группы '
                  'любителей котиков slug будет равен cats: group/cats).',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Текст, описывающий сообщество. Этот текст будет '
                  'отображаться на странице сообщества.'
    )

    class Meta:
        verbose_name = 'Группа для записей'
        verbose_name_plural = 'Группы для записей'

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    """Модель комментариев записи"""

    post = models.ForeignKey(
        Post,
        verbose_name='Запись',
        help_text='Запись, к которой относится комментарий',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария к записи',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:10]


class Follow(models.Model):
    """Модель подписки на авторов"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        help_text='Автор, на которого подписка',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return 'Подписка пользователя {user} на автора {author}'.format(
            user=self.user,
            author=self.author,
        )
