import django_filters as filters

from .models import MyUser


class MyUserFilter(filters.FilterSet):
    recipes = filters.NumberFilter(
        field_name='recipes', method='filter_recipes'
    )

    def filter_recipes(self, queryset, name, value):
        if value:
            print(queryset.objects.all()[:value])
            return queryset.objects.all()[:value]
        return queryset.objects.all()
    
    class Meta:
        model = MyUser
        fields =['recipes']