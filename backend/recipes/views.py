import io
from django.db.models import Sum
from django.http import FileResponse
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.pagination import PageNumberPagination

from users.models import MyUser

from .filters import IngredientFilter, RecipeFilter
from .pdfgen import shopping_list
from .serializers import (
                         IngredientSerializer,
                         TagSerializer,
                         RecipeCreateSerializer,
                         RecipeGetSerializer,
                         ShortRecipeSerializer,
                         Recipe_IngredientGetSerializer,
                         ShoppingCartSerializer,
                         )

from recipes.models import Ingredient, Recipe, Recipe_Ingredient, Tag

myView = (mixins.ListModelMixin, 
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet,)

class LimitSizePagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientView(*myView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = [AllowAny]
    serializer_class = TagSerializer


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitSizePagination
    permission_classes = [AllowAny]
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
            print(self.kwargs)
            if self.kwargs['path']=='favorite':
                user.is_favorite.add(obj)
            else:
                user.is_in_shopping_cart.add(obj)
            serializer = ShortRecipeSerializer(obj)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        if self.kwargs['path']=='favorite':
            user.is_favorite.remove(obj)
        else:
            user.is_in_shopping_cart.remove(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False )
    def download_shopping_cart(self,request):
        ingredients_to_buy = Ingredient.objects.filter(
            recipes__is_in_shopping_cart__id=self.request.user.id
            ).values('name', 'measurement_unit').annotate(
            total_amount=Sum('ingredient__amount')
            )
        txt=''
        for ingredient in ingredients_to_buy.values_list():
            _, name, measure, amount = ingredient
            txt+=f'\u25c7 {name} - {amount} {measure}\n'
        buffer = io.BytesIO()
        mycanvas = canvas.Canvas(buffer)
        shopping_list(mycanvas, txt)
        mycanvas.showPage()
        mycanvas.save()
        buffer.seek(0)
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename="Что_купить.pdf"
            )
        return response

    