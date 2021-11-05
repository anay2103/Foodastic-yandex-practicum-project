from django.contrib.auth.models import AnonymousUser
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import serializers

from .models import Follow, MyUser


class CustomLoginSerializer(TokenCreateSerializer):
    '''
    сериализатор для страницы авторизации,
    переопределяет сериализатор Djoser
    '''
    class Meta:
        model = MyUser
        fields = ['email', 'password']


class CustomUserCreateSerializer(UserCreateSerializer):
    '''
    сериализатор для страницы создания пользователя,
    переопределяет сериализатор Djoser
    '''
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'password']


class CustomUserSerializer(CustomUserCreateSerializer):
    '''
    сериализатор для просмотра списка пользователей,
    к полям родительского класса добавляется поле подписки
    '''
    is_subscribed = serializers.SerializerMethodField()

    class Meta(CustomUserCreateSerializer.Meta):
        fields = CustomUserCreateSerializer.Meta.fields + ['is_subscribed']

    def get_is_subscribed(self, obj):
        if isinstance(
            self.context.get('request', None).user,
            AnonymousUser,
        ):
            return True
        return Follow.objects.filter(
            user=self.context.get('request', None).user,
            following=obj
        ).exists()


class SubscriptionSerializer(CustomUserSerializer):
    '''
    сериализатор для просмотра подписок пользователя,
    к полям родительского класса добавляются
    рецепты избранных авторов и количество рецептов каждого из них
    '''
    recipes = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ['recipes', 'count']

    def get_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        '''импорт внутри метода во избежание кольцевого импорта'''
        from recipes.serializers import RecipeGetSerializer
        fields = ('id', 'name', 'image', 'cooking_time')
        limit = self.context.get(
            'request', None
        ).query_params.get('recipe_limit')
        if limit:
            recipes = obj.recipes.all().order_by('-id')[:int(limit)]
            return RecipeGetSerializer(
                recipes,
                many=True,
                fields=fields,
            ).data
        return RecipeGetSerializer(
            obj.recipes.all(),
            many=True,
            fields=fields,
        ).data
