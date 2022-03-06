from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма записи"""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст новой записи',
            'group': 'Группа, к которой будет относиться запись',
            'image': 'Картинка записи',
        }


class CommentForm(forms.ModelForm):
    """Форма комментария"""

    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите текст вашего комментария'
        }
