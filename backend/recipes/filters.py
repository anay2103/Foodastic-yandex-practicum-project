import django_filters as filters
from recipes.models import Recipe


class IngredientFilter(filters.FilterSet):
    '''фильтр ингредиентов по начальным буквам названия'''
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )


class RecipeFilter(filters.FilterSet):
    '''
    фильтр рецептов по тэгам, автору
    наличию в списке избранного и списке покупок
    '''
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorite', method='filter_is_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart'
    )

    def filter_is_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(
                is_favorite__id=self.request.user.id
            )
        return Recipe.objects.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                is_in_shopping_cart__id=self.request.user.id
            )
        return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart',
                  'tags', 'author']
