from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """Класс для отображения моделей Post в админке"""

    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс для отображения моделей Group в админке"""

    list_display = (
        'title',
        'description',
    )
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    """Класс для отображения моделей Comment в админке"""

    list_display = (
        'text',
        'post',
        'author',
        'created'
    )
    search_fields = ('text',)
    list_filter = ('created', 'author',)


class FollowAdmin(admin.ModelAdmin):
    """Класс для отображения моделей Follow в админке"""

    list_display = (
        'user',
        'author',
    )
    search_fields = ('user',)
    list_filter = ('user', 'author',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
