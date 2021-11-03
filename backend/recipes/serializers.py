import base64
from django.apps import apps
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Ingredient,
                            Tag,
                            Recipe_Ingredient,
                            Recipe)

from users.serializers import CustomUserSerializer

MyUser = apps.get_model('users', 'MyUser')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
     class Meta:
        fields = '__all__'
        model = Tag


class Recipe_IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all(),
        )

    class Meta:
        fields = ['id', 'amount']
        model = Recipe_Ingredient


class Recipe_IngredientGetSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = Recipe_Ingredient


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = Recipe_IngredientGetSerializer(source='recipe', many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)

    class Meta:
        fields = [
                'id', 'tags', 'author', 'ingredients', 
                'name', 'image', 'text', 'cooking_time'
        ]
        model = Recipe
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_favorited'] = instance.is_favorite.filter(
            id=self.context.get('request', None).user.id
            ).exists() #or instance.author.id==self.context.get('request', None).user.id)
        representation['is_in_shopping_cart'] = instance.is_in_shopping_cart.filter(
            id=self.context.get('request', None).user.id
        ).exists() #or instance.author.id==self.context.get('request', None).user.id)
        return representation
    

class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = Recipe_IngredientCreateSerializer(source='recipe', many= True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
             'ingredients', 'tags', 'image', 
             'name', 'text', 'cooking_time'
            ]
        
    def create(self, validated_data):
        ingredients = validated_data.pop('recipe')
        validated_data['author'] = self.context.get('request', None).user
        recipe = super().create(validated_data)
        objs = []
        for ingredient in ingredients:
            data = dict(ingredient)
            objs.append(Recipe_Ingredient(
                recipe=recipe, 
                ingredient=data['ingredient']['id'],
                amount=data['amount'],
            )) 
        Recipe_Ingredient.objects.bulk_create(objs)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe')
        validated_data['author'] = self.context.get('request', None).user
        instance = super().update(instance, validated_data)
        Recipe_Ingredient.objects.filter(recipe=instance).delete()
        objs = []
        for ingredient in ingredients:
            data = dict(ingredient)
            objs.append(Recipe_Ingredient(
                recipe=instance, 
                ingredient=data['ingredient']['id'],
                amount=data['amount'],
            )) 
        Recipe_Ingredient.objects.bulk_create(objs)
        return instance

    def to_representation(self, instance):
        request = self.context['request']
        return RecipeGetSerializer(instance, context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    name =serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Ingredient
    
    def get_total_amount(self, obj):
        amount = Ingredient.objects.filter(
            id=obj.id
        ).annotate(total_amount=Sum('ingredient__amount')).last()
        return amount.total_amount
