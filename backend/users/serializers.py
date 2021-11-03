from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import (TokenCreateSerializer,
                                UserCreateSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import  MyUser, Follow


Recipe = apps.get_model('recipes', 'Recipe')

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
        if isinstance (
            self.context.get('request', None).user,
            AnonymousUser,
            ):
            return True
        return Follow.objects.filter(
            user=self.context.get('request', None).user,
            following=obj
        ).exists()


class UserRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField() 
    name = serializers.ReadOnlyField() 
    image = Base64ImageField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
    
    
class SubscriptionSerializer(CustomUserSerializer):
    recipes =  serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta): 
        fields = CustomUserSerializer.Meta.fields + ['recipes', 'count']
       
    def get_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        limit = self.context.get(
            'request', None
            ).query_params.get('recipe_limit')
        if limit:
            recipes = obj.recipes.all().order_by('-id')[:int(limit)]
            return UserRecipeSerializer(recipes, many=True).data
        return UserRecipeSerializer(obj.recipes.all(), many=True).data
    