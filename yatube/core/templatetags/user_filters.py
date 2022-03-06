from django import template

register = template.Library()


# Добавление класса
@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


# Возврат типа виджета
@register.filter
def widgettype(field):
    return field.field.widget.__class__.__name__
