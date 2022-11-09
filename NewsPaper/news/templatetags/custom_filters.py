from django import template
from ..censor import CENSOR_WORDS

register = template.Library()


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def currency(value):
   """
   value: значение, к которому нужно применить фильтр
   """
   # Возвращаемое функцией значение подставится в шаблон.
   return f'{value} Р'

@register.filter()
def censor(text):
   text_list = text.split()
   for i in range(len(text_list)):
      if text_list[i].upper() in CENSOR_WORDS:
         text_list[i] = f'{text[0]}{"*" * (len(text_list[i]) - 1)}'
   return ' '.join(text_list)

