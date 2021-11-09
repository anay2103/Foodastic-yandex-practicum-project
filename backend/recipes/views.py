import io

from django.core.paginator import InvalidPage
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag

from .filters import IngredientFilter, RecipeFilter
from .pdfgen import shopping_list
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, TagSerializer)

myview = (mixins.ListModelMixin,
          mixins.RetrieveModelMixin,
          viewsets.GenericViewSet,)


class LimitSizePagination(PageNumberPagination):
    page_size_query_param = 'limit'

    def paginate_queryset(self, queryset, request, view=None):
        '''
        метод переопределен чтобы исключить 404 ответ при несоответствии
        номера страницы в запросе и количества отфильтрованных объектов
        '''
        page_size = super().get_page_size(request)
        if not page_size:
            return None
        paginator = super().django_paginator_class(queryset, page_size)
        page_number = super().get_page_number(request, paginator)
        self.request = request
        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            # перенаправляем на первую страницу
            self.page = paginator.page(1)
            return paginator.page(1)
        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        return list(self.page)


class IngredientView(*myview):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagView(*myview):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitSizePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['get', 'delete'],
            url_path='(?P<path>(?:favorite|shopping_cart))')
    def favorite_or_shopping_cart(self, request, pk=None, **kwargs):
        user = self.request.user
        obj = self.get_object()
        if self.request.method == 'GET':
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
