from django.contrib.auth.models import AnonymousUser
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Follow, MyUser


class CustomLoginSerializer(TokenCreateSerializer):
    class Meta:
        model = MyUser
        fields = ['email', 'password']


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'password']


class CustomUserSerializer(CustomUserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(CustomUserCreateSerializer.Meta):
        fields = CustomUserCreateSerializer.Meta.fields + ['is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if isinstance(request.user, AnonymousUser):
            return False
        return Follow.objects.filter(
            user=request.user,
            following=obj
        ).exists()


class UserRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=MyUser.recipes
        )
    name = serializers.ReadOnlyField()
    image = Base64ImageField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = MyUser
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ['recipes', 'count']

    def get_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        limit = request.query_params.get('recipe_limit')
        if not limit:
            return UserRecipeSerializer(
                obj.recipes.all(),
                many=True
            ).data
        return UserRecipeSerializer(
            obj.recipes.all().order_by('-id')[:int(limit)],
            many=True
        ).data
