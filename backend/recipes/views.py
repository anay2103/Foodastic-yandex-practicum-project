import io

from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pdfgen import shopping_list
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, TagSerializer)

myview = (mixins.ListModelMixin,
          mixins.RetrieveModelMixin,
          viewsets.GenericViewSet,)


class LimitSizePagination(PageNumberPagination):
    '''класс для создания кастомной пагинации с параметром limit'''
    page_size_query_param = 'limit'


class IngredientView(*myview):
    '''
    контроллер для просмотра списка ингредиентов и объектов по отдельности
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagView(*myview):
    '''
    контроллер для просмотра списка тэгов и объектов по отдельности
    '''
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer


class RecipeView(viewsets.ModelViewSet):
    '''контроллер рецептов с использованием кастомной пагинации'''
    queryset = Recipe.objects.all()
    pagination_class = LimitSizePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        '''получаем разные сериализаторы для методов GET, CREATE, UPDATE'''
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['get', 'delete'],
            url_path='(?P<path>(?:favorite|shopping_cart))')
    def favorite_or_shopping_cart(self, request, pk=None, **kwargs):
        '''
        единый метод для добавления объекта в избранное или список покупок
        '''
        user = self.request.user
        obj = self.get_object()
        if self.request.method == 'GET':
            print(self.kwargs)
            if self.kwargs['path'] == 'favorite':
                user.is_favorite.add(obj)
            else:
                user.is_in_shopping_cart.add(obj)
            serializer = RecipeGetSerializer(
                obj,
                fields=('id', 'name', 'image', 'cooking_time')
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if self.kwargs['path'] == 'favorite':
            user.is_favorite.remove(obj)
        else:
            user.is_in_shopping_cart.remove(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        '''метод для генерации списка покупок в pdf-формате'''
        ingredients_to_buy = Ingredient.objects.filter(
            recipes__is_in_shopping_cart__id=self.request.user.id
        ).values('name', 'measurement_unit').annotate(
            total_amount=Sum('ingredient__amount')
        )
        txt = ''
        for ingredient in ingredients_to_buy.values_list():
            _, name, measure, amount = ingredient
            txt += f'\u25c7 {name} - {amount} {measure}\n'
        buffer = io.BytesIO()
        mycanvas = canvas.Canvas(buffer)
        shopping_list(mycanvas, txt)
        mycanvas.showPage()
        mycanvas.save()
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename="Что_купить.pdf"
        )
