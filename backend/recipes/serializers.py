from django.contrib.auth.models import AnonymousUser
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class IngredientSerializer(serializers.ModelSerializer):
    '''сериализатор игредиентов'''
    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    '''сериализатор тэгов'''
    class Meta:
        fields = '__all__'
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    сериализатор промежуточной модели между рецептами и количеством
    '''
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all(),
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    def __init__(self, *args, **kwargs):
        '''
        конструктор класса переопределен чтобы динамически определять
        вывод нужных полей с помощью аргумента fields
        '''
        fields = kwargs.pop('fields', None)
        super(RecipeIngredientSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = RecipeIngredient


class RecipeGetSerializer(serializers.ModelSerializer):
    '''сериализатор рецептов для GET-запросов'''
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(source='recipe', many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        '''
        конструктор класса переопределен чтобы динамически определять
        вывод нужных полей с помощью аргумента fields
        '''
        fields = kwargs.pop('fields', None)
        super(RecipeGetSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'is_favorited', 'is_in_shopping_cart',
            'image', 'text', 'cooking_time'
        ]
        model = Recipe

    def get_is_favorited(self, obj):
        if isinstance(
            self.context.get('request', None).user,
            AnonymousUser,
        ):
            return False
        return obj.is_favorite.filter(
            id=self.context.get('request', None).user.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if isinstance(
            self.context.get('request', None).user,
            AnonymousUser,
        ):
            return False
        return obj.is_in_shopping_cart.filter(
            id=self.context.get('request', None).user.id
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''сериализатор рецептов для POST-запросов'''
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

    def create(self, validated_data):
        '''
        метод для создания рецепта переопределен т.к. присутствует
        вложенный сериализатор в поле ingredients
        '''
        ingredients = validated_data.pop('recipe')
        validated_data['author'] = self.context.get('request', None).user
        recipe = super().create(validated_data)
        objs = []
        for ingredient in ingredients:
            data = dict(ingredient)
            objs.append(RecipeIngredient(
                recipe=recipe,
                ingredient=data['ingredient']['id'],
                amount=data['amount'],
            ))
        RecipeIngredient.objects.bulk_create(objs)
        return recipe

    def update(self, instance, validated_data):
        '''
        метод для создания рецепта переопределен т.к. присутствует
        вложенный сериализатор в поле ingredients
        '''
        ingredients = validated_data.pop('recipe')
        validated_data['author'] = self.context.get('request', None).user
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        objs = []
        for ingredient in ingredients:
            data = dict(ingredient)
            objs.append(RecipeIngredient(
                recipe=instance,
                ingredient=data['ingredient']['id'],
                amount=data['amount'],
            ))
        RecipeIngredient.objects.bulk_create(objs)
        return instance

    def to_representation(self, instance):
        '''
        метод переопделен для вывода необходимых полей
        с помощью сериализатора для GET-запросов
        '''
        request = self.context['request']
        return RecipeGetSerializer(instance, context={'request': request}).data
