import django_filters
from .models import *

class AuthorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',lookup_expr='startswith')
    class Meta:
        model = Author
        fields = ['name']



class PostFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name='content',lookup_expr='startswith')
    class Meta:
        model = Post
        fields = ['content']