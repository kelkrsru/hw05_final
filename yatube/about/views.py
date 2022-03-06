from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс для формирования статической страницы Об Авторе"""

    template_name: str = 'about/author.html'


class AboutTechView(TemplateView):
    """Класс для формирования статической страницы Технологии"""

    template_name: str = 'about/tech.html'
