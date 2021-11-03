from django.contrib import admin

from .models import Ingredient, Recipe, Recipe_Ingredient, Tag

class RecipeIngredientInline(admin.TabularInline):
    model = Recipe_Ingredient
    extra = 1 


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name',
        'measurement_unit',)
    list_filter = ('name',)



@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name',
        'author',)
    list_filter = ('name', 'author', 'tags')


@admin.register(Tag)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',)
