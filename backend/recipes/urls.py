from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientView, RecipeView, TagView

router = DefaultRouter()

router.register('ingredients', IngredientView, basename='Ingredient')
router.register('tags', TagView, basename='Tag')
router.register('recipes', RecipeView, basename='Recipe')


urlpatterns = [
    path('', include(router.urls)),
]
