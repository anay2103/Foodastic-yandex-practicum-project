from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from users.serializers import CustomUserSerializer
from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .validators import RecipeCreateValidator


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class SerializerMixin:
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RecipeIngredientSerializer(SerializerMixin, serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all(),
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = RecipeIngredient


class RecipeGetSerializer(SerializerMixin, serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(source='recipe', many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'is_favorited', 'is_in_shopping_cart',
            'image', 'text', 'cooking_time'
        ]
        model = Recipe

    def get_context_handler(self):
        request = self.context.get('request')
        if not request:
            return None
        if request.user.is_anomymous:
            return False
        return request

    def get_is_favorited(self, obj):
        request = self.get_context_handler()
        if not request:
            return None
        return obj.is_favorite.filter(
            id=request.user.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.get_context_handler()
        if not request:
            return None
        return obj.is_in_shopping_cart.filter(
            id=request.user.id
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe',
        many=True,
        fields=('id', 'amount')
    )
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
        validators = [RecipeCreateValidator()]

    def bulk_create(self, ingredients, recipe):
        objs = []
        try:
            for ingredient in ingredients:
                data = dict(ingredient)
                objs.append(RecipeIngredient(
                    recipe=recipe,
                    ingredient=data['ingredient']['id'],
                    amount=data['amount'],
                ))
        except KeyError as error:
            raise ParseError(f'failed to parse the request: {error}')
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe')
        request = self.context.get('request')
        if not request:
            validated_data['author'] = None
        validated_data['author'] = request.user
        recipe = super().create(validated_data)
        self.bulk_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe')
        request = self.context.get('request')
        if not request:
            validated_data['author'] = None
        validated_data['author'] = request.user
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.bulk_create(ingredients, instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(instance, context={'request': request}).data
