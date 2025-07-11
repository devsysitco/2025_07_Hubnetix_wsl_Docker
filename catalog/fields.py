# from django_summernote.fields import SummernoteTextField
# from django.db import models
# import bleach

# class CustomSummernoteTextField(models.TextField):
#     def to_python(self, value):
#         if not value:
#             return value

#         allowed_tags = [
#             'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'h1', 'h2', 'h3',
#             'h4', 'h5', 'h6', 'table', 'tbody', 'thead', 'tr', 'td',
#             'th', 'br', 'hr', 'div', 'span', 'ul', 'ol', 'li', 'img'
#         ]

#         allowed_attributes = {
#             '*': ['class'],
#             'a': ['href', 'target', 'rel'],
#             'img': ['src', 'alt', 'height', 'width'],
#         }

#         return bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)
